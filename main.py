import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
from datetime import time
from zoneinfo import ZoneInfo

# Setup Config
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
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
    """
    This function is called when the bot successfully logs in.
    """
    if not daily_poll.is_running():
        daily_poll.start()
        print("Daily poll task has been started.")

    # Sync the application commands to the specified guild
    if GUILD_ID:
        guild_object = discord.Object(id=GUILD_ID)
        await tree.sync(guild=guild_object)
        print(f"Commands synced to guild {GUILD_ID}")

    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"We are ready to go in, {client.user.name}")

#TODO: Add api/web scraper for national day calendar

# Scheduled Polling 
@tasks.loop(time=time(6, 0, tzinfo=EASTERN))
async def daily_poll():
    """
    A scheduled task to post a poll every day at 6:00 AM EST.
    """
    channel = client.get_channel(POLL_CHANNEL_ID)
    print("It's 6:00 AM, creating a new native daily poll.")

    # Create the native Discord Poll object
    poll = discord.Poll(
        question="good morning 🥰 happy ...",
        answers=["🚀 Productive work session", "🎮 Relax and play some games", "📚 Study or learn something new"],
        duration=28800,  # 8 hours (6 AM to 2 PM)
        allow_multiselect=False
    )

    # Send the poll to the designated channel
    await channel.send(poll=poll)
    
# Bot Commands
@tree.command(
    name="hello",
    description="Say hi",
    guild=discord.Object(id=GUILD_ID)
)

async def test_command(interaction):
    await interaction.response.send_message(f"hi, {interaction.user.mention}")

# Running
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
