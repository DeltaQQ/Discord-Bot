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
        self.m_battleground_lobbies = []
        self.m_lobby_id = 0

        self.m_player_library.load('../data/player_library.json')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.id != self.m_data.m_discord_channels['pg-queue']:
            return

        for lobby in self.m_battleground_lobbies:
            if lobby.m_deploy_message == reaction.message:
                if user.id == lobby.m_lobby_captain.m_discord_id:
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
                    self.m_battleground_lobbies.remove(lobby)

            if lobby.m_ready_message == reaction.message:
                if not (str(user) in lobby.m_team_left or str(user) in lobby.m_team_right):
                    continue

                if str(user) not in lobby.m_ready_player:
                    lobby.m_ready_player.append(str(user))

                if lobby.ready():
                    await lobby.deploy_message(reaction.message.channel)
                    print("Deploy!")

    async def join(self, ctx, *args):
        ingame_name = args[0]
        ingame_class = args[1].lower()

        if ingame_class not in self.m_player_library.m_ingame_class_list:
            print("Invalid class argument")
            raise Exception

        name = str(ctx.message.author)
        rating = self.m_player_library.get_rating(name, ingame_class)

        if not self.m_player_queue.already_in_queue(name):
            print(f"{name} joined the queue")
            player = Player(ctx.author.id, name, ingame_name, ingame_class, rating)
            player.m_in_queue = True
            player.m_queue_join_time = time.time()

            # Schedules a check after one hour to remove idle players from the queue
            task = player.expired(self.m_player_queue, ctx.channel)
            asyncio.create_task(task)

            self.m_player_queue.add_player(player)
        else:
            print(f"{name} is already in the queue")
            await ctx.message.delete()

        if self.m_player_queue.ready_for_matching():
            player_lobby = PlayerLobby(self.m_lobby_id)
            self.m_player_queue.generate_player_lobby(player_lobby)
            player_lobby.balance_teams()

            await player_lobby.ready_message(ctx.channel)
            task = player_lobby.expired(self.m_battleground_lobbies, self.bot.get_channel(self.m_data.m_discord_channels['bg-queue']), self.m_player_queue)
            asyncio.create_task(task)

            self.m_player_library.persist()
            self.m_battleground_lobbies.append(player_lobby)
            print("Lobby is ready!")

    async def leave(self, ctx):
        if self.m_player_queue.already_in_queue(str(ctx.author)):
            self.m_player_queue.remove_player(lambda p: p.m_name == str(ctx.author))
            print(f"{str(ctx.author)} left the queue")

            await ctx.channel.purge(check=lambda m: m.author == ctx.author)
        else:
            await ctx.message.delete()
