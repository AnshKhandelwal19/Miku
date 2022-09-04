from discord.ext import commands
from discord import FFmpegPCMAudio
import discord, pafy, urllib.request, re, random

with open('authcode.txt') as f:
    AUTH_TOKEN = f.readline()

miku = commands.Bot(command_prefix='miku ') #Creates a bot called 'Miku'
miku.remove_command('help') #Removes preset help command

Playlist = []
isLooping = False
shuffle = False

#Non-async methods
def declareVar():
    global isLooping
    global shuffle
    isLooping = False
    shuffle = False

def search(song : str):
    song = song.replace(' ', '+')
    if('youtube.com' in song):
        url = song
    else:
        query = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + song)
        video_ids = re.findall(r"watch\?v=(\S{11})", query.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
    return url

def playNextSong(ctx):
    if not isLooping:
        Playlist.pop(0)
    if shuffle and len(Playlist) > 1:
        s1 = Playlist[0]
        randNum = random.randint(0, len(Playlist)-1)
        Playlist[0] = Playlist[randNum]
        Playlist[randNum] = s1
    if len(Playlist) == 0:
        #asyncio.run_coroutine_threadsafe(ctx.send("There are no more songs Miku can play"))
        return
    else:
        player = FFmpegPCMAudio(Playlist[0].url_https)
        for i in miku.voice_clients:
            i.play(player, after = lambda e : playNextSong(ctx))

def pafyObject(song):
    url = search(song)
    video = pafy.new(url)
    audio = video.getbestaudio()
    return audio

def clearPlaylist():
    global Playlist 
    Playlist = []


#Miku Commands
@miku.command()
async def playlist(ctx):
    if len(Playlist) == 0:
        await ctx.send('Playlist is empty!')
    else:
        await ctx.send('**Current Playlist**')
        count = 1
        for i in Playlist:
            await ctx.send('\t' + str(i+1) + '. ' + str(count) +  i.title)
            count += 1

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

@miku.command()
async def add(ctx, *, song):
    await addSong(ctx, song)

async def addSong(ctx, song):
    audio = pafyObject(song)
    Playlist.append(audio)
    await ctx.send(audio.title + ' has been added to the playlist!')

@miku.command()
async def play(ctx, *, song):
    #Make sure both miku and the user are in a voice channel
    if ctx.message.author.voice == None:
        await ctx.send('You must be in a voice channel for me to join with you')
        return
    elif len(miku.voice_clients) == 0:
        await ctx.author.voice.channel.connect()

    #If a song is already playing
    if ctx.voice_client.is_playing():
        await addSong(ctx, song)
        return

    #If a song is not playing
    elif not ctx.voice_client.is_playing():
        if len(song) > 0:
            global Playlist
            Playlist.insert(0, pafyObject(search(song)))
        else:
            await ctx.send('I cannot play a song I can\'t search!')
            return
    
    #Create an audio player using pafy object and play audio
    player = discord.FFmpegPCMAudio(Playlist[0].url_https)
    print(1)
    await ctx.send('Now playing ' + Playlist[0].title)
    for i in miku.voice_clients:
        i.play(player, after = lambda e : playNextSong(ctx))
        #i.source = discord.PCMVolumeTransformer(i.source, volume=0.2)

@miku.command()
async def pause(ctx):
    if ctx.message.author.voice == None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    if not ctx.voice_client.is_playing():
        if ctx.voice_client.is_paused():
            await ctx.send(Playlist[0].title + ' is already paused')
            return
        else:
            await ctx.send('There is no song currently playing')
            return
    else:
        for i in miku.voice_clients:
            i.pause()

@miku.command()
async def resume(ctx):
    if ctx.message.author.voice == None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    if ctx.voice_client.is_playing():
        ctx.send('Miku is already playing something')
    else:
        if ctx.voice_client.is_paused():
            await ctx.voice_client.resume()
        elif len(Playlist) == 0:
            await ctx.send('There are no songs to play!')
        else:
            await play(ctx, '')

@miku.command()
async def skip(ctx):
    if ctx.message.author.voice == None or len(miku.voice_clients) == 0:
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
    if ctx.message.author.voice == None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    global isLooping
    print(isLooping)
    global shuffle
    print(shuffle)
    if not ctx.voice_client.is_playing():
        await ctx.send('Miku isn\'t playing anything')
    elif isLooping:
        await ctx.send('**' + Playlist[0].title + '** is already looping!')
    else:
        isLooping = True
        shuffle = False

@miku.command()
async def shuffle(ctx):
    if ctx.message.author.voice == None or len(miku.voice_clients) == 0:
        await ctx.send('Miku is not playing anything!')
        return
    global shuffle
    print(shuffle)
    global isLooping
    print(isLooping)

    if not ctx.voice_client.is_playing():
        await ctx.send('Miku isn\'t playing anything')
    elif shuffle:
        await ctx.send('Player is already shuffled!')
    else:
        shuffle = True
        isLooping = False
        await ctx.send('Miku is now shuffle playing :)')


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
        clearPlaylist()

    await miku.process_commands(message)

@miku.event
async def on_command_error(ctx, error): 
    if isinstance(error, commands.CommandNotFound): 
        await ctx.send('Miku cant do that! --> Type \'Miku Help\' to get a list of commands.')

declareVar()
miku.run(AUTH_TOKEN)