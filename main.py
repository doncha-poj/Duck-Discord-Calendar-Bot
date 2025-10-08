import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    print(f"We are ready to go in, {client.user.name}")


@tree.command(
    name="hello",
    description="Say hi",
    guild=discord.Object(id=guild_id)
)
async def test_command(interaction):
    await interaction.response.send_message(f"hi, {interaction.user.mention}")

client.run(token, log_handler=handler, log_level=logging.DEBUG)
