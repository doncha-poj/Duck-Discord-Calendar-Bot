import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
from datetime import time
from zoneinfo import ZoneInfo

# Setup Config
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')
POLL_CHANNEL_ID = int(os.getenv('POLL_CHANNEL_ID', 0))
EASTERN = ZoneInfo("America/New_York")

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Initialization
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Bot Events
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    print(f"We are ready to go in, {client.user.name}")

    # Start any tasks
    if not daily_poll.is_running():
        daily_poll.start()
        print("Daily poll task has been started.")

#FIXME: Add api/web scraper for national day calendar

#FIXME: add polling logic

# Bot Commands
@tree.command(
    name="hello",
    description="Say hi",
    guild=discord.Object(id=guild_id)
)

async def test_command(interaction):
    await interaction.response.send_message(f"hi, {interaction.user.mention}")

# Running
client.run(token, log_handler=handler, log_level=logging.DEBUG)
