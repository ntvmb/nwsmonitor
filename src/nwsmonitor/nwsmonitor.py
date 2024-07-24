"""NWSMonitor bot module."""

import math
import datetime
import logging
import time
import discord
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
):
    await ctx.defer(ephemeral=True)
    _, forecast, real_loc = await nws.get_forecast(location)
    embed = discord.Embed(
        title=f"Forecast for {real_loc.address.removesuffix(', United States')}",
        thumbnail=forecast["icon"][0],
    )
    with StringIO() as desc:
        for period, details in zip(forecast["name"], forecast["detailedForecast"]):
            desc.write(f"{period}: {details}\n")
        embed.description = desc.getvalue()
    await ctx.respond(embed=embed)
