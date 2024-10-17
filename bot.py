# Imports
from discord.ext import commands
import discord
import yt_dlp
import urllib.request
import re
import random
import asyncio

# Create a bot called 'Miku'
miku = commands.Bot(command_prefix='miku ', intents=discord.Intents.all())
miku.remove_command('help')  # Removes preset help command

# Global Variables
Playlist = []
isLooping = False

def declareVar():
    global isLooping
    global shuffle
    isLooping = False
    shuffle = False

# Function to search for YouTube video URLs
def search(song: str):
    song = song.replace(' ', '+')
    if 'youtube.com' in song:
        url = song
    else:
        query = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + song)
        video_ids = re.findall(r"watch\?v=(\S{11})", query.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
    return url

# Function to get the audio stream using yt-dlp
def get_audio_stream(song):
    url = search(song)
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'quiet': True,
        'forcejson': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)  # Get info without downloading
            audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
            
            if not audio_formats:
                raise ValueError("No valid audio formats found.")

            audio_url = audio_formats[0]['url']  # Get the first valid audio URL
            title = info['title']  # Get the title
            return audio_url, title
        except Exception as e:
            print(f"Error retrieving audio stream: {e}")
            return None, None  # Return None values if extraction fails

# Code to add and manage the playlist
async def addSong(ctx, song):
    audio_url, title = get_audio_stream(song)
    Playlist.append({'url': audio_url, 'title': title})
    await ctx.send(f"{title} has been added to the playlist!")

@miku.command()
async def add(ctx, *, song):
    await addSong(ctx, song)

@miku.command()
async def playlist(ctx):
    if len(Playlist) == 0:
        await ctx.send('Playlist is empty!')
    else:
        await ctx.send('**Current Playlist**')
        for count, song in enumerate(Playlist, start=1):
            await ctx.send(f"{count}: {song['title']}")

# Code to control bot
@miku.command()
async def join(ctx):  # Let miku join a voice call with the author
    if ctx.message.author.voice is None:
        await ctx.send('You must be in a voice channel for me to join with you')
        return
    await ctx.author.voice.channel.connect()

@miku.command()
async def leave(ctx):  # Let miku leave the voice call
    if miku.voice_clients:
        for i in miku.voice_clients:
            await i.disconnect()
    else:
        await ctx.send('Miku isn\'t there :)')

def playNextSong(ctx):
    global isLooping
    if not isLooping:
        Playlist.pop(0)  # Remove the first song if not looping

    if len(Playlist) == 0:
        return
    else:
        player = discord.FFmpegPCMAudio(Playlist[0]['url'])  # Ensure you use the .url here
        ctx.voice_client.play(player, after=lambda e: playNextSong(ctx))

@miku.command()
async def play(ctx, *, song):
    if ctx.message.author.voice is None:
        await ctx.send('You must be in a voice channel for me to join with you')
        return

    if len(miku.voice_clients) == 0:
        await ctx.author.voice.channel.connect()
    if ctx.voice_client.is_playing():
        await addSong(ctx, song)
        return

    if len(song) > 0:
        audio_url, title = get_audio_stream(song)
        Playlist.insert(0, {'url': audio_url, 'title': title})  # Insert the audio stream object
    else:
        await ctx.send('I cannot play a song I can\'t search!')
        return

    try:
        player = discord.FFmpegPCMAudio(Playlist[0]['url'])  # Use the correct URL
        await ctx.send(f'Now playing {Playlist[0]["title"]}')
        ctx.voice_client.play(player, after=lambda e: playNextSong(ctx))
    except Exception as e:
        await ctx.send(f'Error playing audio: {str(e)}')

@miku.command()
async def pause(ctx):
    if ctx.message.author.voice is None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    if not ctx.voice_client.is_playing():
        if ctx.voice_client.is_paused():
            await ctx.send(Playlist[0]['title'] + ' is already paused')
            return
        else:
            await ctx.send('There is no song currently playing')
            return
    else:
        for i in miku.voice_clients:
            i.pause()

@miku.command()
async def resume(ctx):
    if ctx.message.author.voice is None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    if ctx.voice_client.is_playing():
        await ctx.send('Miku is already playing something')
    else:
        if ctx.voice_client.is_paused():
            await ctx.voice_client.resume()
        elif len(Playlist) == 0:
            await ctx.send('There are no songs to play!')
        else:
            await play(ctx, '')

@miku.command()
async def skip(ctx):
    if ctx.message.author.voice is None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    global isLooping
    isLooping = False
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    if len(Playlist) == 1:
        await ctx.send('There are no more songs to play!')
    else:
        playNextSong(ctx)

@miku.command()
async def loop(ctx):
    if ctx.message.author.voice is None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    global isLooping
    if not ctx.voice_client.is_playing():
        await ctx.send('Miku isn\'t playing anything')
    elif isLooping:
        await ctx.send('**' + Playlist[0]['title'] + '** is already looping!')
    else:
        isLooping = True
        await ctx.send('Miku is now looping the song ' + Playlist[0]['title'])

# Bot Event Code
@miku.event
async def on_ready():
    print('We have logged in as {0.user}'.format(miku))

@miku.event
async def on_message(message):
    msg = message.content.lower()
    ctx = await miku.get_context(message)

    if message.author.id == 933612749253140511:
        return
    elif msg.startswith('miku add') and len(msg) < 9:
        await ctx.send('You didn\'t tell me what song to add!')
    elif msg == 'miku clear playlist':
        global Playlist 
        Playlist = []
    else:
        await miku.process_commands(message)

@miku.event
async def on_command_error(ctx, error): 
    if isinstance(error, commands.CommandNotFound): 
        await ctx.send('Miku cant do that! --> Type \'Miku Help\' to get a list of commands.')

# Code to run bot
with open('authcode.txt') as f:
    AUTH_TOKEN = f.readline()
declareVar()
miku.run(AUTH_TOKEN)
