import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# @bot.event
# async def on_ready():
#     print(f"We are ready to go in, {bot.user.name}")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id='GUILD_ID'))
    print(f"We are ready to go in, {client.user.name}")

# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server {member.name}")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#
#     if "shit" in message.content.lower():
#         await message.delete()
#         await message.channel.send(f"{message.author.mention} - don't use that word")
#
#     await bot.process_commands(message)

# /hello
# @bot.command()
# async  def hello(ctx):
#     await ctx.send(f"Hello {ctx.author.mention}!")

@tree.command(
    name="hello",
    description="Say hi",
    guild=discord.Object(id='GUILD_ID')
)
async def first_command(interaction):
    await interaction.response.send_message(f"hi, {interaction.user.mention}")

client.run(token, log_handler=handler, log_level=logging.DEBUG)
# bot.run(token, log_handler=handler, log_level=logging.DEBUG)
