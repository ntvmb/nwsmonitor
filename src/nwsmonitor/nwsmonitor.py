"""NWSMonitor bot module."""

import math
import datetime
import logging
import time
import discord
import aiofiles
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
from .uptime import process_uptime_human_readable
from .dir_calc import get_dir
from io import StringIO
from sys import exit

NaN = float("nan")
bot = discord.Bot(intents=discord.Intents.default())
_log = logging.getLogger(__name__)


def kmh_to_mph(kmh: float) -> float:
    return kmh / 1.609344


def celsius_to_fahrenheit(c: float) -> float:
    return c * 1.8 + 32


def mm_to_inch(mm: float) -> float:
    return mm / 25.4


def pa_to_inhg(pa: float) -> float:
    return pa * 0.00029529983071445


@bot.event
async def on_ready():
    watching = discord.Activity(
        type=discord.ActivityType.watching, name="what the clouds are doing"
    )
    await bot.change_presence(activity=watching, status=discord.Status.dnd)
    _log.info(f"Logged in as {bot.user}.")
    global_vars.write("guild_count", len(bot.guilds))


@bot.event
async def on_guild_join(guild: discord.Guild):
    _log.info(f"Bot added to guild {guild.name} (ID: {guild.id})")
    global_vars.write("guild_count", len(bot.guilds))


@bot.event
async def on_guild_remove(guild: discord.Guild):
    logging.info(f"Bot removed from guild {guild.name} (ID: {guild.id})")
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
            logging.exception("Failed to send response.")
        logging.warn(
            f"{ctx.author} attempted to execute {ctx.command.name}, but does not have permission."
        )
    elif isinstance(error, commands.errors.NoPrivateMessage):
        try:
            await ctx.respond(
                "This command cannot be used in a DM context.", ephemeral=True
            )
        except discord.errors.HTTPException:
            logging.exception("Failed to send response.")
    else:
        logging.exception(
            f"An exception occurred while executing {ctx.command.name}.",
            exc_info=(type(error), error, error.__traceback__),
        )
        try:
            await ctx.respond(
                f"An exception occurred while executing this command:\n{error}",
                ephemeral=True,
            )
        except discord.errors.HTTPException:
            logging.exception("Failed to send response.")


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
    location: Option(str, description="Address; City, State; or ZIP code."),
):
    await ctx.defer(ephemeral=True)
    obs = (await nws.get_forecast(location))[0]
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
    wind_dir = "N/A" if wind_dir is None else get_dir(wind_dir)
    wind_speed = obs["windSpeed"]["value"]
    wind_speed_mph = NaN if wind_speed is None else kmh_to_mph(wind_speed)
    wind_gust = obs["windGust"]["value"]
    wind_gust_mph = NaN if wind_gust is None else kmh_to_mph(wind_gust)
    visibility = obs["visibility"]["value"] / 1000
    visibility_mi = NaN if visibility is None else kmh_to_mph(visibility)
    visibility = NaN if visibility is None else visibility
    pressure = obs["barometricPressure"]["value"]
    pressure_inhg = NaN if pressure is None else pa_to_inhg(pressure)
    wind_chill = obs["windChill"]["value"]
    wind_chill_f = NaN if wind_chill is None else celsius_to_fahrenheit(wind_chill)
    heat_index = obs["heatIndex"]["value"]
    heat_index_f = NaN if heat_index is None else celsius_to_fahrenheit(heat_index)
    with StringIO() as desc:
        desc.write(f"Weather: {obs['textDescription']}\n")
        desc.write(f"Temperature: {temp_f:.0f}F ({temp:.0f}C)\n")
        desc.write(f"Dew point: {dew_f:.0f}F ({dew:.0f}C)\n")
        desc.write(f"Humidity: {rh:.0f}%\n")
        desc.write(f"Visibility: {visibility_mi:.2f} mile(s) ({visibility:.2f} km)\n")
        if heat_index is not None:
            desc.write(f"Heat index: {heat_index_f:.0f}F ({heat_index:.0f}C)\n")
        if wind_speed is not None and wind_speed > 0:
            if wind_dir == "N/A":
                wind_dir = "Variable"
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
    await ctx.respond(embed=embed)


@bot.slash_command(
    name="forecast", description="Get the forecast for a location (US only)"
)
async def forecast(
    ctx: discord.ApplicationContext,
    location: Option(str, "Address; City, State; or ZIP code."),
    units: Option(
        str, "Use US or SI units (default: us)", required=False, choices=["us", "si"]
    ) = "us",
):
    await ctx.defer(ephemeral=True)
    _, forecast, real_loc = await nws.get_forecast(location, units)
    embed = discord.Embed(
        title=f"Forecast for {real_loc.address.removesuffix(', United States')}",
        thumbnail=forecast["icon"][0],
    )
    with StringIO() as desc:
        for period, details in zip(forecast["name"], forecast["detailedForecast"]):
            desc.write(f"{period}: {details}\n")
        embed.description = desc.getvalue()
    await ctx.respond(embed=embed)


@bot.slash_command(name="glossary", description="Look up a meteorological term")
async def glossary(
    ctx: discord.ApplicationContext,
    term: Option(str, "The term to look for (in title case)"),
):
    await ctx.defer()
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
                ss.write(f"# {t}\n{d}\n")
            await ctx.respond(ss.getvalue())


@bot.slash_command(name="alerts", description="Look up alerts")
async def alerts(
    ctx: discord.ApplicationContext,
    active: Option(
        bool, description="Only show active alerts (default: True)", required=False
    ) = True,
    start_date: Option(
        str,
        description="Filter by start date/time (ISO format, ignored if active=True)",
        required=False,
    ) = None,
    end_date: Option(
        str,
        description="Filter by end date/time (ISO format, ignored if active=True)",
        required=False,
    ) = None,
    status: Option(
        str,
        description="Alert status",
        choices=["actual", "exercise", "system", "test", "draft"],
        required=False,
    ) = None,
    message_type: Option(
        str,
        description="Filter by message type",
        choices=["alert", "update", "cancel"],
        required=False,
    ) = None,
    event: Option(
        str,
        description="Comma-separated list of alert names",
        required=False,
    ) = None,
    code: Option(
        str,
        description="Comma-separated list of alert codes",
        required=False,
    ) = None,
    location: Option(
        str,
        description="Filter by alert location",
        required=False,
    ) = None,
    urgency: Option(
        str,
        description="Filter alerts by urgency",
        choices=["Immediate", "Expected", "Future", "Past", "Unknown"],
        required=False,
    ) = None,
    severity: Option(
        str,
        description="Filter alerts by severity",
        choices=["Extreme", "Severe", "Moderate", "Minor", "Unknown"],
        required=False,
    ) = None,
    certainty: Option(
        str,
        description="Filter alerts by certainty",
        choices=["Observed", "Likely", "Possible", "Unlikely", "Unknown"],
        required=False,
    ) = None,
    limit: Option(int, description="Limit number of alerts", required=False) = 500,
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
            limit=limit,
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
            limit=limit,
        )
    if not alerts_list.empty:
        async with aiofiles.open("alerts.txt", "w") as fp:
            for head, params, desc, inst in zip(
                alerts_list["headline"],
                alerts_list["parameters"],
                alerts_list["description"],
                alerts_list["instruction"],
            ):
                try:
                    nws_head = params["NWSheadline"][0]
                except KeyError:
                    nws_head = None
                await fp.write(f"{head}\n\n")
                if nws_head:
                    await fp.write(f"{nws_head.center(len(nws_head) + 6, ".")}\n\n")
                if desc:
                    await fp.write(f"{desc}\n\n")
                if inst:
                    await fp.write(f"{inst}\n\n")
                await fp.write("$$\n\n")
        with open("alerts.txt", "rb") as fp:
            await ctx.respond(f"{len(alerts_list)} alert(s) found.", file=discord.File(fp))
    else:
        await ctx.respond("No alerts found with the given parameters.\n\
If looking for older alerts, try using the \
[IEM NWS Text Product Finder](https://mesonet.agron.iastate.edu/wx/afos)."
        )
