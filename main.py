import discord
from discord.ext import tasks
from discord import app_commands, Status
import logging
from dotenv import load_dotenv
import os
from datetime import time, timedelta
from zoneinfo import ZoneInfo
import scraper

# Environment Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID') # For testing purposes

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
    if GUILD_ID: #FIXME: remove block later
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Commands synced to guild: {client.get_guild(int(GUILD_ID)).name}")

    await tree.sync()
    print("Commands synced globally.")

    print(f"{client.user.name} is now online.\n")
    game = discord.Game("with the API")
    await client.change_presence(activity=game)


# Scheduled Polling 
@tasks.loop(time=time(6, 0, tzinfo=EASTERN))
async def daily_poll():
    """A scheduled task to post a poll every day at 6:00 AM EST."""
    print("It's 6:00 AM, creating a new native daily poll.")

    # Find all valid channels across all servers first.
    target_channels = []
    for guild in client.guilds:
        # Logic to find the announcement channel is now directly inside the loop.
        for channel in guild.text_channels:
            if channel.is_news():
                target_channels.append(channel)
                break  # Stop after finding the first one in this guild

    # Exit early if no announcement channels were found.
    if not target_channels:
        print("No announcement channels found in any servers. Skipping poll creation.\n")
        return

    # Fetch answer options with holidays from today
    answer_options = scraper.get_todays_holidays()
    if answer_options:
        answer_options = answer_options[:10]  # Take a slice of the first 10 items


    if not answer_options:
        print("Holiday list is empty. Using fallback list.")

        poll = discord.Poll(
            question="good morning 🥰 rate your morning",
            duration=timedelta(hours=8),  # 8 hours (6 AM to 2 PM)
        )

        answer_options = [
            "5 (Awesome Sauce)",
            "4 (Cool Beans)",
            "3 (Lukewarm)",
            "2 (Ehhh)",
            "1 (sad)"
        ]
    else:
        # Create the native Discord Poll object
        poll = discord.Poll(
            question="good morning 🥰 happy ...",
            duration=timedelta(hours=8),  # 8 hours (6 AM to 2 PM)
        )

    for option in answer_options:
        poll.add_answer(text=option)

    # Send the created poll to all found channels.
    for channel in target_channels:
        await channel.send(poll=poll)
        print(f"Successfully posted poll in '{channel.name}' in server '{channel.guild.name}'.\n")
    
# Bot Commands
@tree.command(name="help", description="list of commands and what they do", guild=discord.Object(id=GUILD_ID))
async def help_command(interaction):
    """A test for slash command"""
    # await interaction.channel.send(f"hey, {interaction.user.mention}")
    await interaction.response.send_message(f"Will implement soon", ephemeral=True)
    print("Successfully sent message\n")

@tree.command(name="hello", description="Say hi", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def hello_command(interaction):
    """A test for slash command"""
    # await interaction.channel.send(f"hey, {interaction.user.mention}")
    await interaction.response.send_message(f"a secret hi to you <3", ephemeral=True)
    print("Successfully sent message\n")

@tree.command(name="emoji", description="Sends a random emoji", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def rand_emoji_command(interaction):
    """A test for sending random emojis"""
    # await interaction.response.send_message(f"hey, {interaction.user.mention}")
    await interaction.response.send_message(f":flushed:", ephemeral=True) #TODO: Get unicode list of emojis
    print("Successfully sent message\n")

@tree.command(name="national-days", description="Lists the national days for today", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def holiday_list_command(interaction):
    """A test for sending random emojis"""
    # await interaction.response.send_message(f"hey, {interaction.user.mention}")
    await interaction.response.send_message(f":flushed:", ephemeral=True) #TODO: Get unicode list of emojis
    print("Successfully sent message\n")

@tree.command(name="poll", description="generate a poll", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def test_poll_command(interaction):
    """Create a test version of the daily poll"""
    print(f"Test poll triggered by {interaction.user.name} in server '{interaction.guild.name}'.")

    # Find the announcement channel in the current server
    target_channel = None
    for channel in interaction.guild.text_channels:
        if channel.is_news():
            target_channel = channel
            break  # Stop after finding the first one

    if not target_channel:
        # If no announcement channel is found, inform the user.
        await interaction.response.send_message(
            "I couldn't find an announcement channel in this server to post the poll.",
            ephemeral=True
        )
        print(f"Failed to find announcement channel in '{interaction.guild.name}'.\n")
        return

    answer_options = [
        "answer1",
        "answer2",
        "answer3"
    ]

    test_poll = discord.Poll(
        question="good morning 🥰 happy ...",
        duration=timedelta(hours=8)  # 8 hours (6 AM to 2 PM)
    )

    for option in answer_options:
        test_poll.add_answer(text=option, emoji=None)

    await target_channel.send(poll=test_poll)
    await interaction.response.send_message("Test poll created successfully, and sent to announcements", ephemeral=True)
    print("Successfully sent test poll\n")

# Running and Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
