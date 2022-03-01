import asyncio
import random
import sys
from copy import deepcopy

from utils import timer
from utils import Data


class PlayerLobby(Data):
    def __init__(self, identifier):
        super().__init__()

        self.m_id = identifier
        self.m_team_left = []
        self.m_team_right = []
        self.m_lobby_captain = None

        self.m_ready_message = None
        self.m_deploy_message = None
        self.m_messages = []
        self.m_ready_player = []

    def set_lobby_captain(self, captain):
        self.m_lobby_captain = captain

    def ready(self):
        if len(self.m_ready_player) == 3:
            return True

        return False

    async def expired(self, player_lobbies, channel):
        await asyncio.sleep(60)

        if not self.ready():
            message = "Lobby expired and will be deleted shortly!"
            emoji = ['😦']

            await self.notify_everyone(channel, message, emoji)
            await self.delete(channel)

            player_lobbies.remove(self)

    async def notify_everyone(self, channel, message, emoji_list=None):
        for user in self.m_team_left + self.m_team_right:
            message += f"<@{user.m_discord_id}>"

        self.m_messages.append(await channel.send(message))

        if emoji_list:
            for emoji in emoji_list:
                await self.m_messages[-1].add_reaction(emoji)

    async def delete(self, channel):
        for index, message in enumerate(self.m_messages):
            await message.delete(delay=10 if index == len(self.m_messages) - 1 else 0)

        await channel.purge(check=lambda m: m.author.id in [p.m_discord_id for p in (self.m_team_right + self.m_team_right)])

    async def ready_message(self, channel):
        message = "Ready? Click on the white checkmark! "
        emoji = '✅'

        for user in self.m_team_left + self.m_team_right:
            message += f"<@{user.m_discord_id}>"

        self.m_ready_message = await channel.send(message)
        self.m_messages.append(self.m_ready_message)

        await self.m_ready_message.add_reaction(emoji)

    async def deploy_message(self, channel):
        deploy_message = "Team Left: "

        for player in self.m_team_left:
            deploy_message += player.m_ingame_name + ", "

        deploy_message = deploy_message[:-2]

        deploy_message += "\nTeam Right: "

        for player in self.m_team_right:
            deploy_message += player.m_ingame_name + ", "

        deploy_message = deploy_message[:-2]

        deploy_message += f"\nLobby Captain: <@{self.m_lobby_captain.m_discord_id}>\n"
        deploy_message += "Please create the lobby and invite everybody!\n"
        deploy_message += f"Report the match result after the game has finished!!! <@{self.m_lobby_captain.m_discord_id}>\n"
        deploy_message += ":regional_indicator_l: Left Team won\n"
        deploy_message += ":regional_indicator_r: Right Team won\n"
        deploy_message += ":x: to abort the match\n"
        deploy_message += ":four_leaf_clover: Good luck!\n"

        self.m_deploy_message = await channel.send(deploy_message)

        emoji = '🍀'
        await self.m_deploy_message.add_reaction(emoji)

        emoji = '🇱'
        await self.m_deploy_message.add_reaction(emoji)

        emoji = '🇷'
        await self.m_deploy_message.add_reaction(emoji)

        emoji = '❌'
        await self.m_deploy_message.add_reaction(emoji)

        await channel.purge(check=lambda m: m.author.id in [p.m_discord_id for p in self.m_team_right + self.m_team_right])

        self.m_messages.append(self.m_deploy_message)

    @timer
    def balance_teams(self):
        player_pool = self.m_team_left + self.m_team_right

        team_left = []
        team_right = []

        count_per_class_dict = {x: 0 for x in self.m_ingame_class_list}

        for player in player_pool:
            count_per_class_dict[player.m_ingame_class] += 1

        class_player_list_dict = {x: [] for x in self.m_ingame_class_list}

        for player in player_pool:
            class_player_list_dict[player.m_ingame_class].append(player)

        minimal_difference = sys.maxsize
        balanced_team_left = []
        balanced_team_right = []

        for i in range(20000):
            team_left.clear()
            team_right.clear()

            for ingame_class in class_player_list_dict:
                if ingame_class == 'nightwalker' or ingame_class == 'warrior':
                    pass
                else:
                    class_player_list_dict[ingame_class] = random.sample(class_player_list_dict[ingame_class], count_per_class_dict[ingame_class])

                    team_left += class_player_list_dict[ingame_class][0:int(count_per_class_dict[ingame_class] / 2)]
                    team_right += class_player_list_dict[ingame_class][int(count_per_class_dict[ingame_class] / 2):count_per_class_dict[ingame_class]]

            eye_list = random.sample(class_player_list_dict['nightwalker'] + class_player_list_dict['warrior'], count_per_class_dict['nightwalker'] + count_per_class_dict['warrior'])

            team_left += eye_list[0:int((count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']) / 2)]
            team_right += eye_list[int((count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']) / 2):count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']]

            team_left_value = 0
            team_right_value = 0

            for player_left, player_right in zip(team_left, team_right):
                team_left_value += player_left.m_rank
                team_right_value += player_right.m_rank

            value_difference = abs(team_left_value - team_right_value)

            if value_difference < minimal_difference:
                balanced_team_left = deepcopy(team_left)
                balanced_team_right = deepcopy(team_right)

                minimal_difference = value_difference

        self.m_team_left = balanced_team_left
        self.m_team_right = balanced_team_right

        sorted_teams = sorted(self.m_team_left, key=lambda p: p.m_rank, reverse=True)
        self.set_lobby_captain(sorted_teams[0])
