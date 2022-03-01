import asyncio
import json

from os import getenv
from discord.ext import commands
from discord.utils import get

from music_queue import MusicQueue
from youtube_manager import YoutubeManager

from player_library import PlayerLibrary
from player_queue import PlayerQueue
from player_lobby import PlayerLobby
from rating_system import update_rating


discord_client = commands.Bot(command_prefix='.', help_command=None)


youtube_manager = YoutubeManager(getenv('YOUTUBE_API_KEY'))
music_queue = MusicQueue()

player_library = PlayerLibrary()
player_library.load('player_library.json')

player_queue = PlayerQueue()

lobby_id = 0
player_lobbies = []


# This has to be somewhere else
with open('discord_channels.json') as json_file:
    discord_channels = json.load(json_file)


async def on_update():
    first_post = True

    while True:
        if youtube_manager.channel_is_live('Cover'):
            if first_post:
                print("Cover is live!")
                url = youtube_manager.current_stream_url
                message = youtube_manager.m_youtube_channels['Cover']['message'] + "\n" + str(url)
                channel_id = discord_channels['cover-live']

                await send_message_to_channel(channel_id, message)
                first_post = False
        else:
            first_post = True

        await asyncio.sleep(5)


async def send_message_to_channel(channel_id, message):
    channel = discord_client.get_channel(channel_id)
    await channel.send(message)


# Events


@discord_client.event
async def on_ready():
    print("Successfully logged in as {0.user}".format(discord_client))
    discord_client.loop.create_task(on_update())


@discord_client.event
async def on_message(message):
    if message.author.bot:
        return

    await discord_client.process_commands(message)


@discord_client.event
async def on_reaction_add(reaction, user):
    for lobby in player_lobbies:
        if lobby.m_deploy_message == reaction.message:
            if user.id == lobby.m_lobby_captain.m_discord_id:
                if reaction.emoji == '🇱':
                    update_rating(player_library, lobby.m_team_left, lobby.m_team_right)
                    await player_library.print_leaderboard(discord_client.get_channel(discord_channels['battleground']))

                if reaction.emoji == '🇷':
                    update_rating(player_library, lobby.m_team_right, lobby.m_team_left)
                    await player_library.print_leaderboard(discord_client.get_channel(discord_channels['battleground']))

                if reaction.emoji == '❌':
                    message = "Match aborted! Please register in the queue again! "
                    await lobby.notify_everyone(reaction.message.channel, message)

                await lobby.delete(reaction.message.channel)
                player_lobbies.remove(lobby)

        if lobby.m_ready_message == reaction.message:
            if not(str(user) in lobby.m_team_left or str(user) in lobby.m_team_right):
                continue

            if str(user) not in lobby.m_ready_player:
                lobby.m_ready_player.append(str(user))

            if lobby.ready():
                await lobby.deploy_message(reaction.message.channel)
                print("Deploy!")


# Commands


@discord_client.command()
async def join(ctx, ingame_name=None, ingame_class=None):
    if ctx.message.channel.id == discord_channels['bg-queue']:
        ingame_class = ingame_class.lower()

        if ingame_class not in player_library.m_ingame_class_list:
            print("Invalid class argument")
            return

        name = str(ctx.message.author)
        rating = player_library.get_rank(name, ingame_class)

        if not player_queue.already_in_queue(name) or True:
            print(f"{name} joined the queue")
            player_queue.add_player(ctx.message.author.id, name, ingame_name, ingame_class, rating)

        if player_queue.ready_for_matching():
            player_lobby = PlayerLobby(lobby_id)
            player_queue.generate_player_lobby(player_lobby)
            player_lobby.balance_teams()

            await player_lobby.ready_message(ctx.channel)
            task = player_lobby.expired(player_lobbies, discord_client.get_channel(discord_channels['bg-queue']))
            asyncio.create_task(task)

            player_library.persist()
            player_lobbies.append(player_lobby)
            print("Lobby is ready!")

    if ctx.message.channel.id == discord_channels['bot-commands']:
        if is_connected_to_channel(ctx):
            await ctx.voice_client.disconnect()

        channel = ctx.message.author.voice.channel
        await channel.connect()

        music_queue.set_voice_client(get(ctx.bot.voice_clients, guild=ctx.guild))


@discord_client.command()
async def leave(ctx):
    if ctx.channel.id == discord_channels['bot-commands']:
        if not is_connected_to_channel(ctx):
            return

        await ctx.voice_client.disconnect()

    if ctx.channel.id == discord_channels['bg-queue']:
        if player_queue.already_in_queue(str(ctx.author)):
            player_queue.remove_player(lambda p: p.m_name == str(ctx.author))
            print(f"{str(ctx.author)} left the queue")

            await ctx.channel.purge(check=lambda m: m.author == ctx.author)


@discord_client.command()
async def submit(ctx, url):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    music_queue.submit_url(url)


@discord_client.command()
async def play(ctx):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice_client.is_playing():
        print("Already playing!")
        return

    music_queue.play()


@discord_client.command()
async def pause(ctx):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

    if not voice_client.is_playing():
        return

    voice_client.pause()


@discord_client.command()
async def resume(ctx):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice_client.is_paused():
        voice_client.resume()


@discord_client.command()
async def skip(ctx):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    voice_client.stop()


@discord_client.command()
async def clear(ctx):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    music_queue.clear()


@discord_client.command()
async def loop(ctx, url, repeat_count):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    for i in range(int(repeat_count)):
        music_queue.submit_url(url)


@discord_client.command()
async def rank(ctx, ingame_class):
    if ctx.channel.id != discord_channels['bot-commands']:
        return

    message = f"Your current rating on {ingame_class} is {player_library.get_rank(str(ctx.author), ingame_class)} <@{ctx.author.id}>"
    await ctx.channel.send(message)


@discord_client.command()
async def purge(ctx):
    if ctx.author.top_role.name != 'Admin':
        return

    await ctx.channel.purge()


# Helpers


def is_connected_to_channel(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


discord_client.run(getenv('DISCORD_TOKEN'))
youtube_manager.shutdown()
