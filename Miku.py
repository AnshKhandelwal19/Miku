from discord.ext import commands
import discord

with open('authcode.txt') as f:
    AUTH_TOKEN = f.readline()

miku = commands.Bot(command_prefix='miku ') #Creates a bot called 'Miku'
miku.remove_command('help') #Removes preset help command

@miku.event
async def on_ready():
  print('We have logged in as {0.user}'.format(miku))

miku.run(AUTH_TOKEN)