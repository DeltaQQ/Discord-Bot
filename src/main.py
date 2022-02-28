import json
import time
import _thread

from os import getenv
from discord.ext import commands
from discord.utils import get

from music_queue import MusicQueue
from youtube_manager import YoutubeManager

from player_library import PlayerLibrary
from player_queue import PlayerQueue
from player_lobby import PlayerLobby


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


@discord_client.event
async def on_reaction_add(reaction, user):
    for lobby in player_lobbies:
        if lobby.m_deploy_message == reaction.message:
            if user.id == lobby.m_lobby_captain.m_discord_id:
                if reaction.emoji == '🇱':
                    # Adjust ranks and clear the lobby
                    pass

                if reaction.emoji == '🇷':
                    # Adjust ranks and clear the lobby
                    pass

                if reaction.emoji == '❌':
                    # Clear the lobby
                    pass

                await lobby.m_ready_message.delete(delay=3)
                await lobby.m_deploy_message.delete()

        if lobby.m_ready_message == reaction.message:
            if str(user) not in lobby.m_team_left or str(user) not in lobby.m_team_right:
                continue

            if str(user) not in lobby.m_ready_player or True:
                lobby.m_ready_player.append(str(user))

            if lobby.ready() and not lobby.expired():
                channel = reaction.message.channel

                deploy_message = ""
                deploy_message += "Team Left: "

                for player in lobby.m_team_left:
                    deploy_message += player.m_ingame_name + ", "

                deploy_message = deploy_message[:-2]

                deploy_message += "\nTeam Right: "

                for player in lobby.m_team_right:
                    deploy_message += player.m_ingame_name + ", "

                deploy_message = deploy_message[:-2]

                deploy_message += f"\nLobby Captain: <@{lobby.m_lobby_captain.m_discord_id}>\n"
                deploy_message += "Please create the lobby and invite everybody!\n"
                deploy_message += f"Report the match result after the game has finished!!! <@{lobby.m_lobby_captain.m_discord_id}>\n"
                deploy_message += ":regional_indicator_l: Left Team won\n"
                deploy_message += ":regional_indicator_r: Right Team won\n"
                deploy_message += ":x: to abort the match\n"
                deploy_message += ":four_leaf_clover: Good luck!\n"

                lobby.m_deploy_message = await channel.send(deploy_message)

                emoji = '🍀'
                await lobby.m_deploy_message.add_reaction(emoji)

                emoji = '🇱'
                await lobby.m_deploy_message.add_reaction(emoji)

                emoji = '🇷'
                await lobby.m_deploy_message.add_reaction(emoji)

                emoji = '❌'
                await lobby.m_deploy_message.add_reaction(emoji)

                await channel.purge(check=lambda m: m.author.id in [p.m_discord_id for p in lobby.m_team_right + lobby.m_team_right])

                lobby.deploy()
                print("Deploy!")


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


@discord_client.command()
async def queue(ctx, ingame_name, ingame_class):
    if ctx.message.channel.id != discord_channels['bg-queue']:
        return

    if ingame_class not in player_library.m_ingame_class_list:
        print("Invalid class argument")
        return

    name = str(ctx.message.author)
    rank = player_library.get_rank(name, ingame_class)

    if not player_queue.already_in_queue(name):
        player_queue.add_player(ctx.message.author.id, name, ingame_name, ingame_class, rank)

    if player_queue.ready_for_matching():
        player_lobby = PlayerLobby(lobby_id)
        player_queue.generate_player_lobby(player_lobby)
        player_lobby.balance_teams()

        message = "Ready? Click on the white checkmark! "
        for user in player_lobby.m_team_left + player_lobby.m_team_right:
            message += f"<@{user.m_discord_id}>"

        player_lobby.m_ready_message = await ctx.send(message)

        emoji = '✅'
        await player_lobby.m_ready_message.add_reaction(emoji)

        player_library.persist()
        player_lobbies.append(player_lobby)
        print("Lobby is ready!")


# Helpers


def is_connected_to_channel(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


discord_client.run(getenv('DISCORD_TOKEN'))
youtube_manager.shutdown()
