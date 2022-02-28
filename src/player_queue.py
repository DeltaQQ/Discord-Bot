import random
import sys
import time
from copy import deepcopy


def timer(function):
    def wrapper(*arg, **kwargs):
        t1 = time.time()
        function(*arg, **kwargs)
        t2 = time.time()
        print(function.__name__, 'took', t2 - t1, 's')
    return wrapper


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

    def add_player(self, name, ingame_name, ingame_class, rank):
        player = Player(name, ingame_name, ingame_class, rank)
        self.m_available_players.append(player)

    def remove_player(self, condition):
        index = self.find(condition)
        self.m_available_players.pop(index)

    def avaiable_class_count(self):
        class_count = {x: 0 for x in self.m_ingame_class_list}

        for player in self.m_available_players:
            class_count[player.m_ingame_class] += 1

        return class_count

    def set_lobby_captain(self, captain):
        self.m_lobby_captain = captain

    def generate_teams(self):
        if len(self.m_available_players) < 10:
            print("Not enough available players!")
            return

        class_count = self.avaiable_class_count()

        # Priest selection

        if class_count['Priest'] == 2:
            index = self.find(lambda player: player.m_ingame_class == 'Priest')
            self.m_team_left.append(self.m_available_players.pop(index))

            index = self.find(lambda player: player.m_ingame_class == 'Priest')
            self.m_team_right.append(self.m_available_players.pop(index))

        # Eye selection

        i = 0
        number_of_eyes = min(int((class_count['Nightwalker'] + class_count['Warrior']) / 2) * 2, 4)

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

        number_of_archers = min(int((class_count['Archer']) / 2) * 2, 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'Archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

        # Mage selection

        number_of_mages = min(int((class_count['Mage']) / 2) * 2, (5 - len(self.m_team_left)) * 2)

        for i in range(number_of_mages):
            index = self.find(lambda player: player.m_ingame_class == 'Mage')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                self.m_team_right.append(self.m_available_players.pop(index))
            else:
                self.m_team_left.append(self.m_available_players.pop(index))

        # Rest selection

        number_of_archers = min(int((class_count['Archer'] - number_of_archers) / 2) * 2, (5 - len(self.m_team_left)) * 2)

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

        class_count = {x: 0 for x in self.m_ingame_class_list}

        for player in player_pool:
            class_count[player.m_ingame_class] += 1

        players = {x: [] for x in self.m_ingame_class_list}

        for player in player_pool:
            players[player.m_ingame_class].append(player)

        minimal_difference = sys.maxsize
        balanced_team_left = []
        balanced_team_right = []

        for i in range(20000):
            team_left.clear()
            team_right.clear()

            for classes in players:
                if classes == 'Nightwalker' or classes == 'Warrior':
                    pass
                else:
                    players[classes] = random.sample(players[classes], class_count[classes])

                    team_left += players[classes][0:int(class_count[classes] / 2)]
                    team_right += players[classes][int(class_count[classes] / 2):class_count[classes]]

            eye_list = random.sample(players['Nightwalker'] + players['Warrior'], class_count['Nightwalker'] + class_count['Warrior'])

            team_left += eye_list[0:int((class_count['Nightwalker'] + class_count['Warrior']) / 2)]
            team_right += eye_list[int((class_count['Nightwalker'] + class_count['Warrior']) / 2):class_count['Nightwalker'] + class_count['Warrior']]

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
