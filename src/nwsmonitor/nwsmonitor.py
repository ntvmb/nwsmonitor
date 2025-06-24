"""NWSMonitor bot module."""

import math
import datetime
import logging
import time
import discord
import aiofiles
import aiohttp
import asyncio
import textwrap
import pathlib
import json
import numpy as np
from discord import (
    option,
    default_permissions,
    SlashCommandOptionType,
    guild_only,
    Option,
)
from discord.ext import tasks, commands
from . import aio_nws as nws
from . import server_vars
from . import global_vars
from .enums import *
from .uptime import process_uptime_human_readable
from .dir_calc import get_dir
from io import StringIO, BytesIO, BufferedIOBase
from pandas import DataFrame, concat
from typing import Dict, List, Any, Optional
from sys import exit
from markdownify import markdownify as md
from markdownify import MarkdownConverter

here = pathlib.Path(__file__).parent.resolve()
TEST_ALERTS = json.loads((here / "test_alerts.json").read_text())
NaN = float("nan")
bot = discord.Bot(
    intents=discord.Intents.default(),
    default_command_integration_types={
        discord.IntegrationType.guild_install,
        discord.IntegrationType.user_install,
    },
)
settings = bot.create_group(
    "settings",
    "Configure the bot",
    integration_types={discord.IntegrationType.guild_install},
)
filtering = settings.create_subgroup("filtering", "Settings related to filtering")
_log = logging.getLogger(__name__)


def kmh_to_mph(kmh: float) -> float:
    return kmh / 1.609344


def celsius_to_fahrenheit(c: float) -> float:
    return c * 1.8 + 32


def mm_to_inch(mm: float) -> float:
    return mm / 25.4


def pa_to_inhg(pa: float) -> float:
    return pa * 0.00029529983071445


def get_alert_text(*args, **kwargs) -> str:
    params = kwargs["parameters"]
    desc = kwargs["description"]
    inst = kwargs["instruction"]
    with StringIO() as ss:
        try:
            nws_head = params["NWSheadline"][0]
        except KeyError:
            nws_head = None
        if nws_head:
            formatted_nws_head = "\n".join(
                textwrap.wrap(nws_head.center(len(nws_head) + 6, "."))
            )
            ss.write(f"{formatted_nws_head}\n\n")
        if desc:
            ss.write(f"{desc}\n\n")
        if inst:
            ss.write(f"{inst}")
        return ss.getvalue()


def is_civ(params: dict):
    orig = params.get("EAS-ORG", [""])[0]
    return orig == "CIV"


@bot.event
async def on_ready():
    watching = discord.Activity(
        type=discord.ActivityType.watching, name="what the clouds are doing"
    )
    await bot.change_presence(activity=watching, status=discord.Status.dnd)
    _log.info(f"Logged in as {bot.user}.")
    global_vars.write("guild_count", len(bot.guilds))
    bot.add_cog(NWSMonitor(bot))


@bot.event
async def on_disconnect():
    _log.warning("Client disconnected.")
    bot.remove_cog("NWSMonitor")


@bot.event
async def on_resumed():
    _log.info("Resumed session.")
    if bot.get_cog("NWSMonitor") is None and bot.is_ready():
        bot.add_cog(NWSMonitor(bot))


@bot.event
async def on_guild_join(guild: discord.Guild):
    _log.info(f"Bot added to guild {guild.name} (ID: {guild.id})")
    global_vars.write("guild_count", len(bot.guilds))


@bot.event
async def on_guild_remove(guild: discord.Guild):
    _log.info(f"Bot removed from guild {guild.name} (ID: {guild.id})")
    server_vars.remove_guild(guild.id)
    global_vars.write("guild_count", len(bot.guilds))


@bot.event
async def on_application_command_error(
    ctx: discord.ApplicationContext, error: Exception
):
    if isinstance(error, commands.errors.MissingPermissions) or isinstance(
        error, commands.errors.NotOwner
    ):
        try:
            await ctx.respond(
                "You do not have permission to use this command. This incident will be reported.",
                ephemeral=True,
            )
        except discord.errors.HTTPException:
            _log.exception("Failed to send response.")
        _log.warning(
            f"{ctx.author} attempted to execute {ctx.command.name}, but does not have permission."
        )
    elif isinstance(error, commands.errors.NoPrivateMessage):
        try:
            await ctx.respond(
                "This command cannot be used in a DM context.", ephemeral=True
            )
        except discord.errors.HTTPException:
            _log.exception("Failed to send response.")
    else:
        _log.exception(
            f"An exception occurred while executing {ctx.command.name}.",
            exc_info=(type(error), error, error.__traceback__),
        )
        try:
            await ctx.respond(
                f"An exception occurred while executing this command:\n{error}",
                ephemeral=True,
            )
        except discord.errors.HTTPException:
            _log.exception("Failed to send response.")


class NWSMonitor(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        _log.info("Starting monitor...")
        self.update_alerts.start()
        self.update_spc_feeds.start()

    def cog_unload(self):
        _log.info("Stopping monitor...")
        self.update_alerts.cancel()
        self.update_spc_feeds.cancel()

    @tasks.loop(minutes=1)
    async def update_alerts(self, test_id: Optional[str] = None):
        if test_id is None:
            is_test = False
            prev_alerts_list = global_vars.get("prev_alerts_list")
            alerts_list = await nws.alerts()
            cancelled_alerts = await nws.alerts(active=False, message_type="cancel")
            alerts_list = concat((alerts_list, cancelled_alerts))
        else:
            is_test = True
            prev_alerts_list = {}
            alerts_list = TEST_ALERTS[test_id]
        new_alerts = []
        e_ids = set()
        e_text_dict = {}
        if prev_alerts_list is None and test_id is None:
            async with aiofiles.open("alerts_.txt", "w") as fp:
                await _write_alerts_list(fp, alerts_list)
            for guild in self.bot.guilds:
                channel_id = server_vars.get("monitor_channel", guild.id)
                if channel_id is not None:
                    await send_alerts(
                        guild.id, channel_id, alert_count=len(alerts_list)
                    )
        else:
            if test_id is None:
                prev_alerts_list = DataFrame(prev_alerts_list)
                prev_ids_array = prev_alerts_list["id"].array
            else:
                prev_ids_array = []
            for guild in self.bot.guilds:
                new_alerts = []
                emergencies = []
                excluded_alerts = server_vars.get("exclude_alerts", guild.id)
                excluded_wfos = server_vars.get("exclude_wfos", guild.id)
                wfo_list = server_vars.get("wfo_list", guild.id)
                if excluded_alerts is None:
                    excluded_alerts = []
                if excluded_wfos is None:
                    excluded_wfos = []
                for i, ad, se, o, en, mt, ev, sn, hl, d, ins, p, ex, st in zip(
                    alerts_list["id"],
                    alerts_list["areaDesc"],
                    alerts_list["sent"],
                    alerts_list["onset"],
                    alerts_list["ends"],
                    alerts_list["messageType"],
                    alerts_list["event"],
                    alerts_list["senderName"],
                    alerts_list["headline"],
                    alerts_list["description"],
                    alerts_list["instruction"],
                    alerts_list["parameters"],
                    alerts_list["expires"],
                    alerts_list["status"],
                ):
                    if (
                        i not in prev_ids_array
                        and not (
                            sn in excluded_wfos
                            or ev in excluded_alerts
                            or ev == AlertType.TEST.value
                        )
                        and (is_civ(p) or sn in WFO)
                        and ((not wfo_list) or sn in wfo_list)
                    ):
                        entry = {
                            "id": i,
                            "areaDesc": ad,
                            "sent": se,
                            "onset": o,
                            "ends": en,
                            "messageType": mt,
                            "event": ev,
                            "senderName": sn,
                            "headline": hl,
                            "description": d,
                            "instruction": ins,
                            "parameters": p,
                            "expires": ex,
                            "status": st,
                        }
                        is_test = st != "Actual"
                        if is_emergency(p, ev):
                            emergencies.append(entry)
                            if i not in e_ids:
                                if i not in e_text_dict:
                                    e_text_dict[i] = get_alert_text(**entry)
                                    e_text = e_text_dict[i]
                                    async with aiofiles.open("bulletin.txt", "w") as f:
                                        await f.write(e_text)
                                with open("bulletin.txt", "rb") as fp:
                                    if is_tore(p):
                                        await send_bulletin(
                                            f"**TORNADO EMERGENCY** for {ad}! \
If you are in the affected area, take immediate tornado precautions!",
                                            fp,
                                            True,
                                            is_test,
                                        )
                                    if is_ffwe(p):
                                        await send_bulletin(
                                            f"**FLASH FLOOD EMERGENCY** for {ad}! \
If you are in the affected area, seek higher ground now!",
                                            fp,
                                            True,
                                            is_test,
                                        )
                                    if (
                                        ev == AlertType.TSW.value
                                        and get_alert_status(p, mt)
                                        != ValidTimeEventCodeVerb.CAN.value
                                    ):
                                        await send_bulletin(
                                            f"A **TSUNAMI WARNING** is in \
effect for {ad}! If you are in the affected area, get away from the coast! \
Move inland, seek higher ground, and stay away from the coast until it is \
deemed safe by local officials.",
                                            fp,
                                            True,
                                            is_test,
                                        )
                                e_ids.add(i)
                        else:
                            new_alerts.append(entry)
                    if not (sn in WFO or i in prev_ids_array):
                        _log.warning(
                            f"Unknown WFO {sn} in alert {i}. Ignoring this alert."
                        )
                new_alerts = DataFrame(new_alerts)
                emergencies = DataFrame(emergencies)
                _log.debug(f"New alerts: {new_alerts}")
                _log.debug(f"New emergencies: {emergencies}")
                channel_id = server_vars.get("monitor_channel", guild.id)
                if channel_id is not None:
                    # avoid rate limiting
                    if len(new_alerts) > 5:
                        async with aiofiles.open("alerts_.txt", "w") as fp:
                            await _write_alerts_list(fp, new_alerts)
                        await send_alerts(
                            guild.id, channel_id, alert_count=len(new_alerts)
                        )
                    else:
                        await send_alerts(guild.id, channel_id, new_alerts)
                    await send_alerts(guild.id, channel_id, emergencies)
        if test_id is None:
            global_vars.write("prev_alerts_list", alerts_list.to_dict("list"))

    @update_alerts.error
    async def on_update_alerts_error(self, error: Exception):
        _log.exception(
            "An error occurred while getting or sending alerts.",
            exc_info=(type(error), error, error.__traceback__),
        )
        self.update_alerts.restart()

    @tasks.loop(minutes=1)
    async def update_spc_feeds(self):
        prev_spc_feed = global_vars.get("prev_spc_feed")
        prev_wpc_feed = global_vars.get("prev_wpc_feed")
        spc_feed = await nws.spc.fetch_spc_feed()
        wpc_feed = await nws.spc.fetch_wpc_feed()
        if prev_spc_feed is None or prev_wpc_feed is None:
            global_vars.write("prev_spc_feed", spc_feed.to_dict("list"))
            global_vars.write("prev_wpc_feed", wpc_feed.to_dict("list"))
            return
        new_articles_spc = []
        new_articles_wpc = []
        prev_spc_feed = DataFrame(prev_spc_feed)
        prev_wpc_feed = DataFrame(prev_wpc_feed)
        prev_dates_array_spc = prev_spc_feed["pubdate"].array
        for t, l, de, da in zip(
            spc_feed["title"],
            spc_feed["link"],
            spc_feed["description"],
            spc_feed["pubdate"],
        ):
            if da not in prev_dates_array_spc:
                new_articles_spc.append(
                    {
                        "title": t,
                        "link": l,
                        "description": de,
                        "pubdate": da,
                    }
                )
        new_articles_spc = DataFrame(new_articles_spc)
        if new_articles_spc.empty:
            _log.info("No SPC articles to send.")
        prev_dates_array_wpc = prev_wpc_feed["pubdate"].array
        for t, l, de, da in zip(
            wpc_feed["title"],
            wpc_feed["link"],
            wpc_feed["description"],
            wpc_feed["pubdate"],
        ):
            if da not in prev_dates_array_wpc:
                new_articles_wpc.append(
                    {
                        "title": t,
                        "link": l,
                        "description": de,
                        "pubdate": da,
                    }
                )
        new_articles_wpc = DataFrame(new_articles_wpc)
        if new_articles_wpc.empty:
            _log.info("No WPC articles to send.")
        for guild in self.bot.guilds:
            channel_id = server_vars.get("spc_channel", guild.id)
            if len(new_articles_spc) > 5:
                async with aiofiles.open("articles.txt", "w") as fp:
                    await _write_article_list(fp, new_articles_spc)
                if channel_id is not None:
                    await send_articles(
                        guild.id, channel_id, article_count=len(new_articles_spc)
                    )
            else:
                if channel_id is not None:
                    await send_articles(guild.id, channel_id, new_articles_spc)
            channel_id = server_vars.get("wpc_channel", guild.id)
            if len(new_articles_wpc) > 5:
                async with aiofiles.open("articles.txt", "w") as fp:
                    await _write_article_list(fp, new_articles_wpc)
                if channel_id is not None:
                    await send_articles(
                        guild.id, channel_id, article_count=len(new_articles_wpc)
                    )
            else:
                if channel_id is not None:
                    await send_articles(guild.id, channel_id, new_articles_wpc)
        global_vars.write("prev_spc_feed", spc_feed.to_dict("list"))
        global_vars.write("prev_wpc_feed", wpc_feed.to_dict("list"))

    @update_spc_feeds.error
    async def on_spc_update_error(self, error: Exception):
        _log.exception(
            "An exception occurred while getting or sending articles.",
            exc_info=(type(error), error, error.__traceback__),
        )
        self.update_spc_feeds.restart()


def get_alert_status(params: dict, m_type: str) -> str:
    try:
        vtec = params["VTEC"][0].strip("/").split(".")
    except (KeyError, AttributeError, TypeError):
        vtec = None
    if vtec is not None:
        m_verb = ValidTimeEventCodeVerb[vtec[1]].value
    else:
        if m_type == "Alert":
            m_verb = ValidTimeEventCodeVerb.NEW.value
        elif m_type == "Update":
            m_verb = ValidTimeEventCodeVerb.default.value
        else:
            m_verb = ValidTimeEventCodeVerb.CAN.value
    return m_verb


def is_tore(params: dict):
    tor_damage_threat = params.get("tornadoDamageThreat", [""])[0]
    return tor_damage_threat == "CATASTROPHIC"


def is_ffwe(params: dict):
    ff_damage_threat = params.get("flashFloodDamageThreat", [""])[0]
    return ff_damage_threat == "CATASTROPHIC"


def is_emergency(params: dict, alert_type: Optional[str] = None):
    return (
        is_tore(params)
        or is_ffwe(params)
        or alert_type == AlertType.EWW.value
        or alert_type == AlertType.TSW.value
    )


async def _write_alerts_list(fp: aiofiles.threadpool.AsyncTextIOWrapper, al: DataFrame):
    for head, params, desc, inst in zip(
        al["headline"],
        al["parameters"],
        al["description"],
        al["instruction"],
    ):
        await fp.write(f"{head}\n\n")
        await fp.write(
            get_alert_text(parameters=params, description=desc, instruction=inst)
        )
        await fp.write("\n\n$$\n\n")


def is_not_in_effect(verb: str) -> bool:
    return (
        verb == ValidTimeEventCodeVerb.CAN.value
        or verb == ValidTimeEventCodeVerb.UPG.value
        or verb == ValidTimeEventCodeVerb.EXP.value
    )


async def send_alerts(
    guild_id: int,
    to_channel: int,
    alerts: Optional[DataFrame] = None,
    alert_count: Optional[int] = 0,
):
    _log.info(f"Sending alerts to guild {guild_id}...")
    channel = bot.get_channel(to_channel)
    if channel is None:
        return
    if alerts is None:
        with open("alerts_.txt", "rb") as fp:
            await channel.send(
                f"{alert_count} alerts were issued or updated.",
                file=discord.File(fp, "alerts.txt"),
            )
    else:
        for i, alert in enumerate(alerts.to_numpy()):
            desc = alert[9]
            inst = alert[10]
            params = alert[11]
            sender_name = alert[7]
            m_type = alert[5]
            event = alert[6]
            sent = alert[2]
            onset = alert[3]
            areas = alert[1]
            exp = alert[12]
            end = alert[4]
            head = alert[8]
            status = alert[13]
            _log.debug(f"{desc=}")
            _log.debug(f"{inst=}")
            if event == AlertType.TEST.value:
                continue

            if not isinstance(params, dict):
                _log.warning("Found malformed alert parameters.")

            m_verb = get_alert_status(params, m_type)

            try:
                tornado = params["tornadoDetection"][0]
            except (KeyError, TypeError):
                tornado = None
            try:
                tor_damage_threat = params["tornadoDamageThreat"][0]
            except (KeyError, TypeError):
                tor_damage_threat = None
            try:
                wind_threat = params["windThreat"][0]
            except (KeyError, TypeError):
                wind_threat = None
            try:
                max_wind = params["maxWindGust"][0]
            except (KeyError, TypeError):
                max_wind = None
            try:
                hail_threat = params["hailThreat"][0]
            except (KeyError, TypeError):
                hail_threat = None
            try:
                max_hail = params["maxHailSize"][0]
            except (KeyError, TypeError):
                max_hail = None
            try:
                tstm_damage_threat = params["thunderstormDamageThreat"][0]
            except (KeyError, TypeError):
                tstm_damage_threat = None
            try:
                flash_flood = params["flashFloodDetection"][0]
            except (KeyError, TypeError):
                flash_flood = None
            try:
                ff_damage_threat = params["flashFloodDamageThreat"][0]
            except (KeyError, TypeError):
                ff_damage_threat = None
            try:
                snow_squall = params["snowSquallDetection"][0]
            except (KeyError, TypeError):
                snow_squall = None
            try:
                snow_squall_impact = params["snowSquallImpact"][0]
            except (KeyError, TypeError):
                snow_squall_impact = None

            if event == AlertType.TOR.value and tor_damage_threat == "CONSIDERABLE":
                event = SpecialAlert.PDS_TOR.value
            elif event == AlertType.TOR.value and tor_damage_threat == "CATASTROPHIC":
                event = SpecialAlert.TOR_E.value
            elif event == AlertType.FFW.value and ff_damage_threat == "CATASTROPHIC":
                event = SpecialAlert.FFW_E.value
            elif event == AlertType.SVR.value and tstm_damage_threat == "DESTRUCTIVE":
                event = SpecialAlert.PDS_SVR.value

            # "isTest" IS NOT AN OFFICIAL PARAMETER
            if isinstance(params, dict):
                is_test = params.get("isTest", False)
            else:
                is_test = False

            if not is_test:
                is_test = status != "Actual"

            emoji = DEFAULT_EMOJI.get(event, ":warning:")

            with StringIO() as ss:
                if is_test:
                    ss.write("**THIS IS ONLY A TEST**\n")
                ss.write(f"{sender_name} {m_verb} ")
                if not is_not_in_effect(m_verb):
                    ss.write(f"{emoji} ")
                ss.write(f"{event} ")
                if (
                    tornado is not None
                    or max_wind is not None
                    or max_hail is not None
                    or flash_flood is not None
                    or ff_damage_threat is not None
                    or tstm_damage_threat is not None
                    or snow_squall is not None
                ):
                    ss.write("(")
                    if tornado is not None:
                        ss.write(f"tornado: {tornado}, ")
                    if tor_damage_threat is not None:
                        ss.write(f"damage threat: {tor_damage_threat}, ")
                    if tstm_damage_threat is not None:
                        ss.write(f"damage threat: {tstm_damage_threat}, ")
                    if flash_flood is not None:
                        ss.write(f"flash flood: {flash_flood}, ")
                    if ff_damage_threat is not None:
                        ss.write(f"damage threat: {ff_damage_threat}, ")
                    if max_wind is not None:
                        ss.write(f"wind: {max_wind}")
                        if wind_threat is not None:
                            ss.write(f" ({wind_threat})")
                        ss.write(", ")
                    if max_hail is not None:
                        ss.write(f'hail: {max_hail}"')
                        if hail_threat is not None:
                            ss.write(f" ({hail_threat})")
                        ss.write(", ")
                    if snow_squall is not None:
                        ss.write(f"snow squall: {snow_squall}, ")
                    if snow_squall_impact is not None:
                        ss.write(f"impact: {snow_squall_impact}, ")
                    ss.seek(ss.tell() - 2)  # go back 2 characters
                    ss.write(") ")
                if sent != onset and onset is not None:
                    onset = int(datetime.datetime.fromisoformat(onset).timestamp())
                    ss.write(f"valid <t:{onset}:f> ")
                if (
                    m_verb == ValidTimeEventCodeVerb.EXA.value
                    or m_verb == ValidTimeEventCodeVerb.EXB.value
                ):
                    ss.write(f"to include {areas} ")
                else:
                    ss.write(f"for {areas} ")
                if not (
                    is_not_in_effect(m_verb)
                    or event in STR_ALERTS_WITH_NO_END_TIME
                    or not (event in AlertType or event in SpecialAlert)
                ):
                    if end is not None:
                        end = int(datetime.datetime.fromisoformat(end).timestamp())
                        ss.write(f"until <t:{end}:f>.")
                    elif (
                        event == AlertType.SPS.value
                        or event == AlertType.MWS.value
                        or event == AlertType.AQA.value
                    ):
                        exp = int(datetime.datetime.fromisoformat(exp).timestamp())
                        ss.write(f"until <t:{exp}:f>.")
                    else:
                        ss.write(f"until further notice.")
                ss.seek(ss.tell() - 1)
                ss.write(".")
                if is_test:
                    ss.write("\n**THIS IS ONLY A TEST. NO ACTION IS REQUIRED.**")
                text = ss.getvalue()
            try:
                nws_head = params["NWSheadline"][0]
            except KeyError:
                nws_head = None
            async with aiofiles.open(f"alert{i}.txt", "w") as b:
                await b.write(
                    get_alert_text(
                        parameters=params, description=desc, instruction=inst
                    )
                )
            # I don't know if discord.File supports aiofiles objects
            with open(f"alert{i}.txt", "rb") as fp:
                if len(text) > 2000:
                    await channel.send(
                        f"NWSMonitor tried to send a message that was too long. \
Here's a shortened version:\n{head}",
                        file=discord.File(fp),
                    )
                else:
                    await channel.send(text, file=discord.File(fp))


async def _write_article_list(
    fp: aiofiles.threadpool.AiofilesContextManager, al: DataFrame
):
    for t, l, d in zip(al["title"], al["link"], al["pubdate"]):
        await fp.write(f"{d}\n{t}\n{l}\n\n")


async def send_articles(
    guild_id: int,
    to_channel: int,
    articles: Optional[DataFrame] = None,
    article_count: Optional[int] = 0,
):
    _log.info(f"Sending articles to channel {to_channel}...")
    channel = bot.get_channel(to_channel)
    if channel is None:
        return
    if articles is None:
        with open("articles.txt", "rb") as fp:
            await channel.send(
                f"{article_count} articles were sent.",
                file=discord.File(fp),
            )
    else:
        for i, article in enumerate(articles.to_numpy()):
            title = article[0]
            link = article[1]
            desc = article[2]
            date = article[3]
            async with aiofiles.open(f"article{i}.txt", "w") as b:
                await b.write(desc)
            text = f"{title}\n{link}"
            with open(f"article{i}.txt", "rb") as fp:
                if len(text) > 2000:
                    await channel.send(
                        f"NWSMonitor tried to send a message that was too long. \
Here's a shortened version:\n{link}",
                        file=discord.File(fp),
                    )
                await channel.send(text, file=discord.File(fp))


@bot.slash_command(name="ping", description="Pong!")
async def ping(ctx: discord.ApplicationContext):
    await ctx.defer()
    await ctx.respond(f"Pong! `{bot.latency * 1000:.0f} ms`")


@bot.slash_command(
    name="current_conditions",
    description="Get current conditions for a location (US Only)",
)
async def current_conditions(
    ctx: discord.ApplicationContext,
    location: Option(str, description="Address; City, State; or ZIP code."),  # type: ignore
):
    await ctx.defer()
    obs = (await nws.get_forecast(location))[0]
    alerts = await nws.alerts_for_location(location, status="actual")
    station_name = obs["station"][-4:]
    embed = discord.Embed(
        title=f"Current conditions at {station_name}",
        thumbnail=obs["icon"],
        timestamp=datetime.datetime.fromisoformat(obs["timestamp"]),
    )
    temp = obs["temperature"]["value"]
    temp_f = NaN if temp is None else celsius_to_fahrenheit(temp)
    temp = NaN if temp is None else temp
    dew = obs["dewpoint"]["value"]
    dew_f = NaN if dew is None else celsius_to_fahrenheit(dew)
    dew = NaN if dew is None else dew
    rh = obs["relativeHumidity"]["value"]
    rh = NaN if rh is None else rh
    wind_dir = obs["windDirection"]["value"]
    wind_dir = "Variable" if wind_dir is None else get_dir(wind_dir)
    wind_speed = obs["windSpeed"]["value"]
    wind_speed_mph = NaN if wind_speed is None else kmh_to_mph(wind_speed)
    wind_gust = obs["windGust"]["value"]
    wind_gust_mph = NaN if wind_gust is None else kmh_to_mph(wind_gust)
    visibility = obs["visibility"]["value"]
    visibility = None if visibility is None else visibility / 1000
    visibility_mi = NaN if visibility is None else kmh_to_mph(visibility)
    visibility = NaN if visibility is None else visibility
    pressure = obs["barometricPressure"]["value"]
    pressure_inhg = NaN if pressure is None else pa_to_inhg(pressure)
    wind_chill = obs["windChill"]["value"]
    wind_chill_f = NaN if wind_chill is None else celsius_to_fahrenheit(wind_chill)
    heat_index = obs["heatIndex"]["value"]
    heat_index_f = NaN if heat_index is None else celsius_to_fahrenheit(heat_index)
    msg = ""
    with StringIO() as desc:
        desc.write(f"Weather: {obs['textDescription']}\n")
        desc.write(f"Temperature: {temp_f:.0f}F ({temp:.0f}C)\n")
        desc.write(f"Dew point: {dew_f:.0f}F ({dew:.0f}C)\n")
        desc.write(f"Humidity: {rh:.0f}%\n")
        desc.write(f"Visibility: {visibility_mi:.2f} mile(s) ({visibility:.2f} km)\n")
        if heat_index is not None:
            desc.write(f"Heat index: {heat_index_f:.0f}F ({heat_index:.0f}C)\n")
        if wind_speed is not None and wind_speed > 0:
            desc.write(
                f"Wind: {wind_dir} at {wind_speed_mph:.0f} mph ({wind_speed:.0f} km/h)\n"
            )
        else:
            desc.write("Wind: Calm\n")
        if wind_gust is not None:
            desc.write(f"Gusts: {wind_gust_mph:.0f} mph ({wind_gust:.0f} km/h)\n")
        if wind_chill is not None:
            desc.write(f"Wind chill: {wind_chill_f:.0f}F ({wind_chill:.0f}C)\n")
        if pressure is not None:
            desc.write(
                f"Pressure: {pressure_inhg:.2f} in. Hg ({pressure / 100:.0f} mb)\n"
            )
        embed.description = desc.getvalue()
    if not alerts.empty:
        with StringIO() as alerts_desc:
            if len(alerts) == 1:
                alerts_desc.write("There is 1 alert in effect for this location:\n")
            else:
                alerts_desc.write(
                    f"There are {len(alerts)} alerts in effect for this location:\n"
                )
            for ev, se, on, ed in zip(
                alerts["event"],
                alerts["sent"],
                alerts["onset"],
                alerts["ends"],
            ):
                alerts_desc.write(f"{ev}")
                if se != on and on is not None:
                    onset_ts = int(datetime.datetime.fromisoformat(on).timestamp())
                    alerts_desc.write(f" in effect from <t:{onset_ts}:f>")
                if ed is not None:
                    end_ts = int(datetime.datetime.fromisoformat(ed).timestamp())
                    alerts_desc.write(f" until <t:{end_ts}:f>")
                alerts_desc.write("\n")
            msg = alerts_desc.getvalue()
    if msg:
        await ctx.respond(msg, embed=embed)
    else:
        await ctx.respond(embed=embed)


@bot.slash_command(
    name="forecast", description="Get the forecast for a location (US only)"
)
async def forecast(
    ctx: discord.ApplicationContext,
    location: Option(str, "Address; City, State; or ZIP code."),  # type: ignore
    units: Option(
        str, "Use US or SI units (default: us)", required=False, choices=["us", "si"]
    ) = "us",  # type: ignore
):
    await ctx.defer()
    _, forecast, real_loc = await nws.get_forecast(location, units)
    alerts = await nws.alerts_for_location(location, status="actual")
    embed = discord.Embed(
        title=f"Forecast for {real_loc.address.removesuffix(', United States')}",
        thumbnail=forecast["icon"][0],
    )
    msg = ""
    with StringIO() as desc:
        for period, details in zip(forecast["name"], forecast["detailedForecast"]):
            desc.write(f"{period}: {details}\n")
        embed.description = desc.getvalue()
    if not alerts.empty:
        with StringIO() as alerts_desc:
            if len(alerts) == 1:
                alerts_desc.write("There is 1 alert in effect for this location:\n")
            else:
                alerts_desc.write(
                    f"There are {len(alerts)} alerts in effect for this location:\n"
                )
            for ev, se, on, ed in zip(
                alerts["event"],
                alerts["sent"],
                alerts["onset"],
                alerts["ends"],
            ):
                alerts_desc.write(f"{ev}")
                if se != on and on is not None:
                    onset_ts = int(datetime.datetime.fromisoformat(on).timestamp())
                    alerts_desc.write(f" in effect from <t:{onset_ts}:f>")
                if ed is not None:
                    end_ts = int(datetime.datetime.fromisoformat(ed).timestamp())
                    alerts_desc.write(f" until <t:{end_ts}:f>")
                alerts_desc.write("\n")
            msg = alerts_desc.getvalue()
    if msg:
        await ctx.respond(msg, embed=embed)
    else:
        await ctx.respond(embed=embed)


@bot.slash_command(name="glossary", description="Look up a meteorological term")
async def glossary(
    ctx: discord.ApplicationContext,
    term: Option(str, "The term to look for (in title case)"),  # type: ignore
):
    try:
        await ctx.defer()
    except discord.errors.InteractionResponded:
        pass
    gloss = await nws.glossary()
    terms = gloss[gloss["term"] == term]
    if terms.empty:
        await ctx.respond(
            "Term not found. (Check your spelling!)\n\
Note: Terms are case-sensitive. Try using title case!"
        )
    else:
        with StringIO() as ss:
            for t, d in zip(terms["term"], terms["definition"]):
                ss.write(f"# {t}\n{md(d, sup_symbol="^")}\n")
            msg = ss.getvalue()
            await ctx.respond(msg)


@bot.slash_command(name="random_glossary", description="Define a random glossary term")
async def random_glossary(ctx: discord.ApplicationContext):
    await ctx.defer()
    gloss = await nws.glossary()
    term = gloss["term"].sample(1).to_numpy()[0]
    await ctx.invoke(glossary, term)


@bot.slash_command(name="alerts", description="Look up alerts")
async def alerts(
    ctx: discord.ApplicationContext,
    active: Option(
        bool, description="Only show active alerts (default: True)", required=False
    ) = True,  # type: ignore
    start_date: Option(
        str,
        description="Filter by start date/time (ISO format, ignored if active=True)",
        required=False,
    ) = None,  # type: ignore
    end_date: Option(
        str,
        description="Filter by end date/time (ISO format, ignored if active=True)",
        required=False,
    ) = None,  # type: ignore
    status: Option(
        str,
        description="Alert status",
        choices=["actual", "exercise", "system", "test", "draft"],
        required=False,
    ) = None,  # type: ignore
    message_type: Option(
        str,
        description="Filter by message type",
        choices=["alert", "update", "cancel"],
        required=False,
    ) = None,  # type: ignore
    event: Option(
        str,
        description="Comma-separated list of alert names",
        required=False,
    ) = None,  # type: ignore
    code: Option(
        str,
        description="Comma-separated list of alert codes",
        required=False,
    ) = None,  # type: ignore
    location: Option(
        str,
        description="Filter by alert location",
        required=False,
    ) = None,  # type: ignore
    urgency: Option(
        str,
        description="Filter alerts by urgency",
        choices=["Immediate", "Expected", "Future", "Past", "Unknown"],
        required=False,
    ) = None,  # type: ignore
    severity: Option(
        str,
        description="Filter alerts by severity",
        choices=["Extreme", "Severe", "Moderate", "Minor", "Unknown"],
        required=False,
    ) = None,  # type: ignore
    certainty: Option(
        str,
        description="Filter alerts by certainty",
        choices=["Observed", "Likely", "Possible", "Unlikely", "Unknown"],
        required=False,
    ) = None,  # type: ignore
):
    await ctx.defer()
    if start_date:
        start_date = datetime.datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.datetime.fromisoformat(end_date)
    if location:
        alerts_list = await nws.alerts_for_location(
            location,
            active=active,
            start=start_date,
            end=end_date,
            status=status,
            message_type=message_type,
            event=event,
            code=code,
            urgency=urgency,
            severity=severity,
            certainty=certainty,
        )
    else:
        alerts_list = await nws.alerts(
            active=active,
            start=start_date,
            end=end_date,
            status=status,
            message_type=message_type,
            event=event,
            code=code,
            urgency=urgency,
            severity=severity,
            certainty=certainty,
        )
    _log.debug(f"{alerts_list=}")
    if not alerts_list.empty:
        async with aiofiles.open("alerts.txt", "w") as fp:
            await _write_alerts_list(fp, alerts_list)
        with open("alerts.txt", "rb") as fp:
            await ctx.respond(
                f"{len(alerts_list)} alert(s) found.", file=discord.File(fp)
            )
    else:
        await ctx.respond(
            "No alerts found with the given parameters.\n\
If looking for older alerts, try using the \
[IEM NWS Text Product Finder](https://mesonet.agron.iastate.edu/wx/afos)."
        )


@settings.command(
    name="alert_channel",
    description="Set the channel to send new alerts to",
)
@guild_only()
@commands.has_guild_permissions(manage_channels=True)
async def set_alert_channel(
    ctx: discord.ApplicationContext,
    channel: Option(discord.TextChannel, description="The channel to use"),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    if channel.permissions_for(ctx.me).send_messages:
        server_vars.write("monitor_channel", channel.id, ctx.guild_id)
        await ctx.respond(f"Successfully set the alert channel to {channel}!")
    else:
        await ctx.respond(
            f"I cannot send messages to that channel.\n\
Give me permission to post in said channel, or use a different channel."
        )


@filtering.command(
    name="exclude_wfo",
    description="Exclude alerts from a WFO",
)
@guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def exclude_wfo(
    ctx: discord.ApplicationContext,
    wfo: Option(
        str,
        description="The WFO to exclude",
        autocomplete=discord.utils.basic_autocomplete(
            [w.value for w in WFO if w != WFO.AAQ]
        ),
    ),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    exclusions = server_vars.get("exclude_wfos", ctx.guild_id)
    if isinstance(exclusions, list):
        if wfo not in exclusions:
            exclusions.append(wfo)
        else:
            await ctx.respond(f"{wfo} is already excluded.")
            return
    else:
        exclusions = [wfo]
    server_vars.write("exclude_wfos", exclusions, ctx.guild_id)
    await ctx.respond(f"Added {wfo} to the exclusion list.")


@filtering.command(
    name="exclude_alert",
    description="Exclude an alert type",
)
@guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def exclude_alert(
    ctx: discord.ApplicationContext,
    alert: Option(
        str,
        description="The alert to exclude",
        autocomplete=discord.utils.basic_autocomplete(
            [a.value for a in AlertType if a not in REQUIRED_ALERTS]
        ),
    ),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    exclusions = server_vars.get("exclude_alerts", ctx.guild_id)
    if isinstance(exclusions, list):
        if set(exclusions).issuperset(STR_ALERTS - STR_SVR_ALERTS):
            await ctx.respond("This command cannot be used in SVR WX mode.")
            return
        if alert not in exclusions:
            exclusions.append(alert)
        else:
            await ctx.respond(f'"{alert}" is already excluded.')
            return
    else:
        exclusions = [alert]
    server_vars.write("exclude_alerts", exclusions, ctx.guild_id)
    await ctx.respond(f'Added "{alert}" to the exclusion list.')


@filtering.command(
    name="exclude_marine_alerts",
    description="Shortcut to exclude all marine alerts",
)
@guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def exclude_marine_alerts(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    exclusions = server_vars.get("exclude_alerts", ctx.guild_id)
    if isinstance(exclusions, list):
        if set(exclusions).issuperset(STR_ALERTS - STR_SVR_ALERTS):
            await ctx.respond("This command cannot be used in SVR WX mode.")
            return
        # Working with a set here ensures that there are no duplicate
        # elements.
        exclusions = set(exclusions).update({a.value for a in MARINE_ALERTS})
        exclusions = list(exclusions)
    else:
        exclusions = [a.value for a in MARINE_ALERTS]
    server_vars.write("exclude_alerts", exclusions, ctx.guild_id)
    await ctx.respond(
        "Added all marine alerts to the exclusion list. Note: Only alert \
types that are exclusively issued in marine locations are excluded."
    )


@filtering.command(
    name="clear_filters",
    description="Clear ALL filters (This cannot be undone!)",
)
@guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def clear_filters(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    server_vars.write("exclude_wfos", None, ctx.guild_id)
    server_vars.write("exclude_alerts", None, ctx.guild_id)
    server_vars.write("exclude_alerts_old", None, ctx.guild_id)
    server_vars.write("wfo_list", None, ctx.guild_id)
    await ctx.respond("Cleared all filters.")


@filtering.command(
    name="only_from_wfo",
    description="Only send alerts from (a) certain WFO(s)",
)
@guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def only_from_wfo(
    ctx: discord.ApplicationContext,
    wfo: Option(
        str,
        "The WFO to add",
        autocomplete=discord.utils.basic_autocomplete([w.value for w in WFO]),
    ),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    exclusions = server_vars.get("exclude_wfos", ctx.guild_id)
    wfo_list = server_vars.get("wfo_list", ctx.guild_id)
    if isinstance(wfo_list, list):
        if isinstance(exclusions, list) and wfo in exclusions:
            await ctx.respond("Cannot use an excluded WFO.")
            return
        wfo_list.append(wfo)
    else:
        wfo_list = [wfo]
    server_vars.write("wfo_list", wfo_list, ctx.guild_id)
    await ctx.respond(f"Added {wfo} to the WFO list.")


@filtering.command(
    name="svrwx_mode",
    description="Toggle SVR WX mode (Only send required "
    "alerts and those related to severe weather)",
)
@guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def svrwx_mode(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    exclusions = server_vars.get("exclude_alerts", ctx.guild_id)
    if isinstance(exclusions, list):
        if set(exclusions).issuperset(STR_ALERTS - STR_SVR_ALERTS):
            exclusions = server_vars.get("exclude_alerts_old", ctx.guild_id)
        else:
            server_vars.write("exclude_alerts_old", exclusions, ctx.guild_id)
            # Working with a set here ensures that there are no duplicate
            # elements.
            exclusions = set(exclusions)
            exclusions.update(STR_ALERTS - STR_SVR_ALERTS)
            exclusions = {a.value for a in exclusions if isinstance(a, AlertType)}
            exclusions = list(exclusions)
    else:
        server_vars.write("exclude_alerts_old", exclusions, ctx.guild_id)
        exclusions = set(AlertType) - SVR_ALERTS
        exclusions = [a.value for a in exclusions]
    server_vars.write("exclude_alerts", exclusions, ctx.guild_id)
    if isinstance(exclusions, list) and set(exclusions).issuperset(
        STR_ALERTS - STR_SVR_ALERTS
    ):
        await ctx.respond("Activated SVR WX mode.")
    else:
        await ctx.respond("Deactivated SVR WX mode.")


@settings.command(
    name="show",
    description="Show current settings",
)
@guild_only()
async def show_settings(ctx: discord.ApplicationContext):
    await ctx.defer()
    alert_channel = server_vars.get("monitor_channel", ctx.guild_id)
    spc_channel = server_vars.get("spc_channel", ctx.guild_id)
    wpc_channel = server_vars.get("wpc_channel", ctx.guild_id)
    alert_exclusions = server_vars.get("exclude_alerts", ctx.guild_id)
    wfo_exclusions = server_vars.get("exclude_wfos", ctx.guild_id)
    wfo_list = server_vars.get("wfo_list", ctx.guild_id)
    if alert_channel is not None:
        alert_channel = f"<#{alert_channel}>"
    if spc_channel is not None:
        spc_channel = f"<#{spc_channel}>"
    if wpc_channel is not None:
        wpc_channel = f"<#{wpc_channel}>"
    if wfo_list is None:
        wfo_list = "Any"
    if isinstance(alert_exclusions, list) and set(alert_exclusions).issuperset(
        STR_ALERTS - STR_SVR_ALERTS
    ):
        alert_exclusions = "(SVR WX mode)"
    await ctx.respond(
        f"# Settings\n\
Alert channel: {alert_channel}\n\
SPC channel: {spc_channel}\n\
WPC channel: {wpc_channel}\n\
Excluded alerts: {alert_exclusions}\n\
Excluded WFOs: {wfo_exclusions}\n\
Monitoring WFOs: {wfo_list}\n\
Uptime: {process_uptime_human_readable()}"
    )


@settings.command(
    name="spc_channel", description="Set the channel to send SPC products to"
)
@guild_only()
@commands.has_guild_permissions(manage_channels=True)
async def set_spc_channel(
    ctx: discord.ApplicationContext,
    channel: Option(discord.TextChannel, description="The channel to use"),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    if channel.permissions_for(ctx.me).send_messages:
        server_vars.write("spc_channel", channel.id, ctx.guild_id)
        await ctx.respond(f"Successfully set the SPC channel to {channel}!")
    else:
        await ctx.respond(
            f"I cannot send messages to that channel.\n\
Give me permission to post in said channel, or use a different channel."
        )


@settings.command(
    name="wpc_channel", description="Set the channel to send WPC products to"
)
@guild_only()
@commands.has_guild_permissions(manage_channels=True)
async def set_wpc_channel(
    ctx: discord.ApplicationContext,
    channel: Option(discord.TextChannel, description="The channel to use"),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    if channel.permissions_for(ctx.me).send_messages:
        server_vars.write("wpc_channel", channel.id, ctx.guild_id)
        await ctx.respond(f"Successfully set the WPC channel to {channel}!")
    else:
        await ctx.respond(
            f"I cannot send messages to that channel.\n\
Give me permission to post in said channel, or use a different channel."
        )


@bot.slash_command(name="purge", description="Clear all cached data")
@commands.is_owner()
async def purge(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    global_vars.write("prev_alerts_list", None)
    global_vars.write("prev_spc_feed", None)
    global_vars.write("prev_wpc_feed", None)
    await ctx.respond("Cleared cache.")


@settings.command(
    name="bulletin_channel", description="Set the channel for NWSMonitor announcements"
)
@guild_only()
@commands.has_guild_permissions(manage_channels=True)
async def bulletin_channel(
    ctx: discord.ApplicationContext,
    channel: Option(discord.TextChannel, description="The channel to use"),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    if channel.permissions_for(ctx.me).send_messages:
        server_vars.write("bulletin_channel", channel.id, ctx.guild_id)
        await ctx.respond(f"Successfully set the WPC channel to {channel}!")
    else:
        await ctx.respond(
            f"I cannot send messages to that channel.\n\
Give me permission to post in said channel, or use a different channel."
        )


async def send_bulletin(
    message: str,
    attachment: Optional[BufferedIOBase] = None,
    is_automated: bool = False,
    is_test: bool = False,
):
    if is_automated:
        message = "(automated message)\n" + message
    if is_test:
        message = (
            "# THIS IS A TEST\n"
            + message
            + "\n**The above bulletin is only a test. Please disregard.**"
        )
    for guild in bot.guilds:
        if attachment is not None:
            attachment.seek(0)
        channel_id = server_vars.get("bulletin_channel", guild.id)
        if channel_id is None:
            continue
        channel = bot.get_channel(channel_id)
        if channel is None:
            continue
        if attachment is None:
            if len(message) < 2000:
                await channel.send(message)
            else:
                with open("tmp.txt", "wb+") as fp:
                    fp.write(message.encode("utf-8"))
                    fp.seek(0)
                    await channel.send(
                        f"NWSMonitor tried to send a bulletin that was too long. \
The bulletin has been sent as a file.",
                        file=discord.File(fp),
                    )
        else:
            if len(message) < 2000:
                await channel.send(message, file=discord.File(attachment))
            else:
                with open("tmp.txt", "wb+") as fp:
                    fp.write(message.encode("utf-8"))
                    fp.seek(0)
                    await channel.send(
                        f"NWSMonitor tried to send a bulletin that was too long. \
The bulletin has been sent as a file.",
                        files=[discord.File(fp), discord.File(attachment)],
                    )


@bot.slash_command(name="send_bulletin", description="Announce something")
@commands.is_owner()
async def send_bulletin_wrapper(
    ctx: discord.ApplicationContext,
    msg: Option(str, "Bulletin text"),  # type: ignore
    file: Option(discord.Attachment, "File for extra info", required=False),  # type: ignore
):
    try:
        await ctx.defer(ephemeral=True)
    except discord.errors.InteractionResponded:
        pass
    if file is not None:
        with open(file.filename, "wb") as f:
            await file.save(f)
        with open(file.filename, "rb") as f:
            await send_bulletin(msg, f)
    else:
        await send_bulletin(msg)
    await ctx.respond("Bulletin sent!")


@bot.slash_command(
    name="send_bulletin_from_file", description="Announce something from a file"
)
@commands.is_owner()
async def send_bulletin_from_file(
    ctx: discord.ApplicationContext,
    msg: Option(discord.Attachment, "Text file"),  # type: ignore
    extra_file: Option(discord.Attachment, "File for extra info", required=False),  # type: ignore
):
    await ctx.defer(ephemeral=True)
    if not msg.content_type.startswith("text"):
        await ctx.respond("`msg` must be a text file.")
        return

    msg_text = await msg.read()
    msg_text = msg_text.decode("UTF-8")
    await ctx.invoke(send_bulletin_wrapper, msg=msg_text, file=extra_file)


@bot.slash_command(name="resend_alert", description="Resend alert by ID")
@commands.is_owner()
async def resend_alert(
    ctx: discord.ApplicationContext, alert: Option(str, "Alert ID")  # type: ignore
):
    await ctx.defer(ephemeral=True)
    if alert in TEST_ALERTS:
        alert_dict = TEST_ALERTS[alert]
    else:
        alerts_list = global_vars.get("prev_alerts_list")
        if alerts_list is None:
            await ctx.respond("No alerts in cache.")
            return
        alerts_list = DataFrame(alerts_list)
        consolidated_alert = alerts_list[alerts_list["id"] == alert]
        if consolidated_alert.empty:
            await ctx.respond("Alert not found.")
            return
        alert_dict = consolidated_alert.to_dict("list")

    alert_2d_list = [
        [
            alert_dict["id"][0],
            alert_dict["areaDesc"][0],
            alert_dict["sent"][0],
            alert_dict["onset"][0],
            alert_dict["ends"][0],
            alert_dict["messageType"][0],
            alert_dict["event"][0],
            alert_dict["senderName"][0],
            alert_dict["headline"][0],
            alert_dict["description"][0],
            alert_dict["instruction"][0],
            alert_dict["parameters"][0],
            alert_dict["expires"][0],
        ]
    ]
    consolidated_alert = DataFrame(alert_2d_list)

    if alert in TEST_ALERTS:
        cog: NWSMonitor = bot.get_cog("NWSMonitor")
        await cog.update_alerts(test_id=alert)
    else:
        for guild in bot.guilds:
            channel_id = server_vars.get("monitor_channel", guild.id)
            if channel_id is not None:
                await send_alerts(guild.id, channel_id, consolidated_alert)
    await ctx.respond("Alert sent.")
