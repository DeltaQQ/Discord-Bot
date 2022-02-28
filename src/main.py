import time
import _thread

from os import getenv
from discord.ext import commands
from discord.utils import get

from music_queue import MusicQueue
from youtube_manager import YoutubeManager

from player_library import PlayerLibrary
from player_queue import PlayerQueue

discord_client = commands.Bot(command_prefix='.', help_command=None)


youtube_manager = YoutubeManager(getenv('YOUTUBE_API_KEY'))
music_queue = MusicQueue()


def on_update():
    first_post = True

    while True:
        if youtube_manager.channel_is_live('Cover'):
            if first_post:
                print("Cover is live!")
                url = youtube_manager.current_stream_url
                message = youtube_manager.m_youtube_channels['Cover']['message'] + "\n" + str(url)
                channel_id = youtube_manager.m_youtube_channels['Cover']['discordChannelID']

                discord_client.loop.create_task(send_message_to_channel(channel_id, message))
                first_post = False
        else:
            first_post = True

        time.sleep(5)


async def send_message_to_channel(channel_id, message):
    channel = discord_client.get_channel(channel_id)
    await channel.send(message)


# Events


@discord_client.event
async def on_ready():
    print("Successfully logged in as {0.user}".format(discord_client))
    _thread.start_new_thread(on_update, ())


@discord_client.event
async def on_message(message):
    if message.author.bot:
        return

    await discord_client.process_commands(message)


# Commands


@discord_client.command()
async def join(ctx):
    if is_connected_to_channel(ctx):
        await ctx.voice_client.disconnect()

    channel = ctx.message.author.voice.channel
    await channel.connect()

    music_queue.set_voice_client(get(ctx.bot.voice_clients, guild=ctx.guild))


@discord_client.command()
async def leave(ctx):
    if not is_connected_to_channel(ctx):
        return

    await ctx.voice_client.disconnect()


@discord_client.command()
async def submit(ctx, url):
    music_queue.submit_url(url)


@discord_client.command()
async def play(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice_client.is_playing():
        print("Already playing!")
        return

    music_queue.play()


@discord_client.command()
async def pause(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

    if not voice_client.is_playing():
        return

    voice_client.pause()


@discord_client.command()
async def resume(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice_client.is_paused():
        voice_client.resume()


@discord_client.command()
async def skip(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    voice_client.stop()


@discord_client.command()
async def clear(ctx):
    music_queue.clear()


@discord_client.command()
async def loop(ctx, url, repeat_count):
    for i in range(int(repeat_count)):
        music_queue.submit_url(url)


# Helpers


def is_connected_to_channel(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


discord_client.run(getenv('DISCORD_TOKEN'))
youtube_manager.shutdown()
