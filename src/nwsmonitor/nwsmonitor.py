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
from io import StringIO
from sys import exit

bot = discord.Bot(intents=discord.Intents.default())
_log = logging.getLogger(__name__)


def kmh_to_mph(kmh: float) -> float:
    return x * 1.609344


def celsius_to_fahrenheit(c: float) -> float:
    return x * 1.8 + 32


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
