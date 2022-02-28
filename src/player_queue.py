import random
import sys
from copy import deepcopy

from utils import timer


class Player:
    def __init__(self, name, ingame_name, ingame_class, rank):
        self.m_name = name
        self.m_ingame_name = ingame_name
        self.m_ingame_class = ingame_class
        self.m_rank = rank

    def __eq__(self, other):
        return self.m_name == other.m_name


class PlayerQueue:
    def __init__(self):
        self.m_available_players = []
        self.m_team_left = []
        self.m_team_right = []
        self.m_lobby_captain = {}
        self.m_ingame_class_list = ['Mage', 'Archer', 'Priest', 'Nightwalker', 'Warrior']

    def find(self, condition):
        index = 0
        for index, player in enumerate(self.m_available_players):
            if condition(player):
                return index

        return index

    def size(self):
        return len(self.m_available_players)

    def add_player(self, name, ingame_name, ingame_class, rank):
        player = Player(name, ingame_name, ingame_class, rank)
        self.m_available_players.append(player)

    def remove_player(self, condition):
        index = self.find(condition)
        self.m_available_players.pop(index)

    def get_count_per_class_dict(self):
        count_per_class_dict = {x: 0 for x in self.m_ingame_class_list}

        for player in self.m_available_players:
            count_per_class_dict[player.m_ingame_class] += 1

        return count_per_class_dict

    def set_lobby_captain(self, captain):
        self.m_lobby_captain = captain

    def ready_for_matching(self):
        count_per_class_dict = self.get_count_per_class_dict()

        player_count = self.size()

        if player_count < 10:
            print("Not enough players available!")
            return

        if count_per_class_dict['Priest'] == 1 and player_count - 1 < 10:
            print("One Priest missing!")
            return False

        if (count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']) % 2 != 0:
            if player_count - 1 < 10:
                print("One Eye missing!")
                return False

        if count_per_class_dict['Archer'] % 2 != 0:
            if player_count - 1 < 10:
                print("One Archer missing!")
                return False

        if count_per_class_dict['Mage'] % 2 != 0:
            if player_count - 1 < 10:
                print("One Archer missing!")
                return False

        return True

    def generate_teams(self):
        if self.size() < 10:
            print("Not enough players available!")
            return

        count_per_class_dict = self.get_count_per_class_dict()

        # Priest selection

        if count_per_class_dict['Priest'] == 2:
            index = self.find(lambda player: player.m_ingame_class == 'Priest')
            self.m_team_left.append(self.m_available_players.pop(index))

            index = self.find(lambda player: player.m_ingame_class == 'Priest')
            self.m_team_right.append(self.m_available_players.pop(index))

        # Eye selection

        i = 0
        number_of_eyes = min(int((count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']) / 2) * 2, 4)

        for i in range(number_of_eyes):
            index = self.find(lambda player: player.m_ingame_class == 'Nightwalker')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

        for j in range(i + 1, number_of_eyes):
            index = self.find(lambda player: player.m_ingame_class == 'Warrior')
            if index == len(self.m_available_players):
                break

            if j % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

        # Archer selection

        number_of_archers = min(int((count_per_class_dict['Archer']) / 2) * 2, 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'Archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

        # Mage selection

        number_of_mages = min(int((count_per_class_dict['Mage']) / 2) * 2, (5 - len(self.m_team_left)) * 2)

        for i in range(number_of_mages):
            index = self.find(lambda player: player.m_ingame_class == 'Mage')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

        # Rest selection

        number_of_archers = min(int((count_per_class_dict['Archer'] - number_of_archers) / 2) * 2, (5 - len(self.m_team_left)) * 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'Archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

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
        self.m_lobby_captain = sorted_teams[0]

# Testing


player_queue = PlayerQueue()

player_queue.add_player('Cover', 'cover', 'Mage', 1500)
player_queue.add_player('Cover', 'cover', 'Mage', 1500)
player_queue.add_player('Cover', 'cover', 'Mage', 1500)
player_queue.add_player('Cover', 'cover', 'Archer', 1500)
player_queue.add_player('Cover', 'cover', 'Mage', 1500)
player_queue.add_player('Cover', 'cover', 'Mage', 1500)
player_queue.add_player('Cover', 'cover', 'Archer', 3000)
player_queue.add_player('Cover', 'cover', 'Archer', 1500)
player_queue.add_player('Cover', 'cover', 'Archer', 500)
player_queue.add_player('Cover', 'cover', 'Warrior', 1500)
player_queue.add_player('Cover', 'cover', 'Nightwalker', 1500)

if player_queue.ready_for_matching():
    player_queue.generate_teams()
    player_queue.balance_teams()

print("Done")
