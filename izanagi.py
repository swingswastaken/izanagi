from dotenv import load_dotenv
import os
import asyncio

import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Default to test if not set
MODE = os.getenv("BOT_MODE", "test")

# Needed only for testing
GUILD_ID_ENV = os.getenv("GUILD_ID")
GUILD_ID = int(GUILD_ID_ENV) if GUILD_ID_ENV else None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    intents=intents,
    help_command=None
)


async def load_extensions():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    if MODE == "test":
        if GUILD_ID is None:
            raise RuntimeError("GUILD_ID is required in test mode but was not set")

        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"Logged in as {bot.user} (TESTING)")
    else:
        await bot.tree.sync()
        print(f"Logged in as {bot.user} (GLOBAL)")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


asyncio.run(main())