import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
from datetime import time, timedelta
from zoneinfo import ZoneInfo

# Environment Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID') #FIXME: Remove once done
POLL_CHANNEL_ID = int(os.getenv('DISCORD_POLL_CHANNEL_ID', 0)) #FIXME: Remove

# Timezone set to US Eastern
EASTERN = ZoneInfo("America/New_York")

# Initialization
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Bot Events
@client.event
async def on_ready():
    """This function is called when the bot successfully logs in."""
    if not daily_poll.is_running():
        daily_poll.start()
        print("Daily poll task has been started.")

    # Sync the application commands to the specified guild
    if GUILD_ID:
        await tree.sync(guild=discord.Object(id=GUILD_ID)) #FIXME: Remove inside once done testing
        print(f"Commands synced to guild {GUILD_ID}")

    print(f"We are ready to go in, {client.user.name}")

#TODO: Add api/web scraper for national day calendar

# Scheduled Polling 
@tasks.loop(time=time(6, 0, tzinfo=EASTERN))
async def daily_poll():
    """A scheduled task to post a poll every day at 6:00 AM EST."""
    channel = client.get_channel(POLL_CHANNEL_ID)
    print("It's 6:00 AM, creating a new native daily poll.")

    # Create the native Discord Poll object
    poll = discord.Poll(
        question="good morning 🥰 happy ...",
        duration=timedelta(hours=8),  # 8 hours (6 AM to 2 PM)
        multiple=False
    )

    # Send the poll to the designated channel
    await channel.send(poll=poll)
    
# Bot Commands
@tree.command(name="hello", description="Say hi", guild=discord.Object(id=GUILD_ID))
async def test_command(interaction):
    """A test for slash command"""
    await interaction.response.send_message(f"hi, {interaction.user.mention}")

@tree.command(name="poll", description="generate a poll", guild=discord.Object(id=GUILD_ID))
async def test_poll_command(interaction):
    """Create a test version of the daily poll"""

    answer_options = [
        "answer1",
        "answer2",
        "answer3"
    ]

    test_poll = discord.Poll(
        question="good morning 🥰 happy ...",
        duration=timedelta(hours=8),  # 8 hours (6 AM to 2 PM)
        multiple=False
    )

    discord.Message(poll=test_poll)
    await interaction.response.send_message("Test poll created successfully", ephemeral=True)

# Running and Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
