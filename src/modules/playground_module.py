import asyncio
import time

from discord.ext import commands

from src.player_library import PlayerLibrary
from src.rating_system import update_rating
from src.player_queue import PlayerQueue
from src.player_lobby import PlayerLobby
from src.player import Player
from src.utils import Data


class PlaygroundModule(commands.Cog, name='playground-module'):
    def __init__(self, bot):
        self.bot = bot
        self.m_data = Data()
        self.m_player_library = PlayerLibrary()
        self.m_player_queue = PlayerQueue()
        self.m_playground_lobbies = []
        self.m_lobby_id = 0
        self.m_desired_lobby_size = 0

        self.m_player_library.load('../data/player_library.json')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.id != self.m_data.m_discord_channels['pg-queue']:
            return

        for lobby in self.m_playground_lobbies:
            if lobby.m_deploy_message and (lobby.m_deploy_message.id == reaction.message.id):
                if user.id == lobby.m_lobby_captain.m_id:
                    if reaction.emoji == '🇱':
                        update_rating(self.m_player_library, lobby.m_team_left, lobby.m_team_right)
                        self.m_player_library.update_ranking('../data/player_ranking.json')
                    elif reaction.emoji == '🇷':
                        update_rating(self.m_player_library, lobby.m_team_right, lobby.m_team_left)
                        self.m_player_library.update_ranking('../data/player_ranking.json')
                    elif reaction.emoji == '❌':
                        message = "Match aborted! Please register in the queue again! "
                        await lobby.notify_everyone(reaction.message.channel, message)
                    else:
                        return

                    await lobby.delete(reaction.message.channel)
                    self.m_playground_lobbies.remove(lobby)
            elif lobby.m_ready_message.id == reaction.message.id:
                if not lobby.contains(user.id):
                    continue

                if reaction.emoji == '✅':
                    player = lobby.get_player(user.id)

                    if player not in lobby.m_ready_player:
                        lobby.m_ready_player.append(player)

                    if lobby.ready():
                        await lobby.deploy_message(reaction.message.channel)
                        print("Deploy!")

                elif reaction.emoji == '❌':
                    # Re-add every player into the queue
                    for player in (lobby.m_team_right + lobby.m_team_left):
                        self.m_player_queue.add_player(player)

                    # Remove the lobby from the list
                    self.m_playground_lobbies.remove(lobby)

                    # Delete the ready message
                    await reaction.message.delete()

    async def join(self, ctx, *args):
        if len(args) % 2 != 0:
            print("Invalid number of arguments")
            raise Exception

        if not self.m_player_queue.already_in_queue(ctx.author.id):
            print(f"{str(ctx.message.author)} joined the queue")
            player = Player(ctx.author.id)
            player.m_in_queue = True
            player.m_queue_join_time = time.time()
            player.add_characters(self.m_player_library, *args)

            # Schedules a check after one hour to remove idle players from the queue
            task = player.expired(self.m_player_queue, ctx.channel)
            asyncio.create_task(task)

            self.m_player_queue.add_player(player)

            task = self.start_with_current_size(ctx)
            asyncio.create_task(task)
        else:
            print(f"{str(ctx.message.author)} is already in the queue")
            await ctx.message.delete()

    async def leave(self, ctx):
        if self.m_player_queue.already_in_queue(ctx.author.id):
            self.m_player_queue.remove_player(lambda p: p.m_id == ctx.author.id)
            print(f"{str(ctx.author)} left the queue")

            await ctx.channel.purge(check=lambda m: m.author == ctx.author)

            task = self.start_with_current_size(ctx)
            asyncio.create_task(task)
        else:
            await ctx.message.delete()

    async def start_with_current_size(self, ctx):
        current_queue_size = self.m_player_queue.size()

        if current_queue_size < 6:
            print("Not enough players in queue")
            return

        await asyncio.sleep(10)

        if current_queue_size != self.m_player_queue.size():
            return

        # Try to start a match
        i = 0
        for i in range(6, 16, 2):
            if self.m_player_queue.can_make_lobby(i):
                pass
            else:
                break

        if i == 6:
            return

        self.m_player_queue.m_desired_lobby_size -= 2 if i != 14 else 0

        player_lobby = PlayerLobby(self.m_lobby_id)
        self.m_player_queue.generate_player_lobby(player_lobby)
        player_lobby.balance_teams()

        await player_lobby.playground_ready_message(ctx.channel)

        self.m_player_library.persist()
        self.m_playground_lobbies.append(player_lobby)
        print("Lobby is ready!")
