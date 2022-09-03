from discord.ext import commands
import discord

with open('authcode.txt') as f:
    AUTH_TOKEN = f.readline()

miku = commands.Bot(command_prefix='miku ') #Creates a bot called 'Miku'
miku.remove_command('help') #Removes preset help command

#Miku Commands
@miku.command()
async def join(ctx):  #Let miku join a voice call with the author
    if ctx.message.author.voice == None:
        await ctx.send('You must be in a voice channel for me to join with you')
        return
    elif len(miku.voice_clients) == 0:
        await ctx.author.voice.channel.connect()

@miku.command()
async def leave(ctx):  #Let miku leave the voice call
    if miku.voice_clients:
        for i in miku.voice_clients:
            await i.disconnect()
    else:
        await ctx.send('Miku isn\'t there :)')


@miku.event
async def on_ready():
  print('We have logged in as {0.user}'.format(miku))

miku.run(AUTH_TOKEN)