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
        self.m_lobby_captain = {}

        self.m_ready_message = {}
        self.m_deploy_message = {}
        self.m_ready_player = []

    def set_lobby_captain(self, captain):
        self.m_lobby_captain = captain

    def ready(self):
        if len(self.m_ready_player) == 10:
            return True

        return False

    def deploy(self):
        # Deploy the lobby
        pass

    def expired(self):
        # Check if lobby is expired
        pass

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
                if ingame_class == 'Nightwalker' or ingame_class == 'Warrior':
                    pass
                else:
                    class_player_list_dict[ingame_class] = random.sample(class_player_list_dict[ingame_class], count_per_class_dict[ingame_class])

                    team_left += class_player_list_dict[ingame_class][0:int(count_per_class_dict[ingame_class] / 2)]
                    team_right += class_player_list_dict[ingame_class][int(count_per_class_dict[ingame_class] / 2):count_per_class_dict[ingame_class]]

            eye_list = random.sample(class_player_list_dict['Nightwalker'] + class_player_list_dict['Warrior'], count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior'])

            team_left += eye_list[0:int((count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']) / 2)]
            team_right += eye_list[int((count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']) / 2):count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']]

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

        sorted_teams = sorted(self.m_team_left + self.m_team_right, key=lambda p: p.m_rank, reverse=True)
        self.set_lobby_captain(sorted_teams[0])
