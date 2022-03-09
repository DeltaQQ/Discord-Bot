from utils import Data, timer

from player import Player


class PlayerQueue(Data):
    def __init__(self):
        super().__init__()

        self.m_available_players = []
        self.m_desired_lobby_size = 0

    def find(self, condition):
        index = 0
        for index, player in enumerate(self.m_available_players):
            if condition(player):
                return index

        return index

    def size(self):
        return len(self.m_available_players)

    def already_in_queue(self, discord_id):
        for player in self.m_available_players:
            if player.m_id == discord_id:
                return True

        return False

    def add_player(self, player: Player):
        self.m_available_players.append(player)

    def remove_player(self, condition):
        index = self.find(condition)
        self.m_available_players.pop(index)

    def get_count_per_class_dict(self):
        count_per_class_dict = {x: 0 for x in self.m_ingame_class_list}

        for player in self.m_available_players:
            count_per_class_dict[player.get_active_class()] += 1

        return count_per_class_dict

    @timer
    def can_make_lobby(self, lobby_size):
        self.m_desired_lobby_size = lobby_size

        if self.size() < self.m_desired_lobby_size:
            print("Not enough players available!")
            return

        return self.iterate_combinations()

    def iterate_combinations(self, player_index=0):
        if player_index == len(self.m_available_players):
            return self.ready_for_matching()

        for i in range(len(self.m_available_players[player_index].m_characters)):
            self.m_available_players[player_index].set_active_character(i)
            if self.iterate_combinations(player_index + 1):
                return True

        return False

    def ready_for_matching(self):
        count_per_class_dict = self.get_count_per_class_dict()

        player_count = self.size()
        player_needed = self.m_desired_lobby_size

        if count_per_class_dict['priest'] == 1 and player_count - 1 < player_needed:
            print("One Priest missing!")
            return False

        player_count -= count_per_class_dict['priest']

        desired_priest_count = min(4 if self.m_desired_lobby_size >= 12 else 2, int(count_per_class_dict['priest'] / 2) * 2)
        player_needed -= desired_priest_count

        numer_of_eyes = count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']

        if numer_of_eyes % 2 != 0:
            if player_count - 1 < player_needed:
                print("One Eye missing!")
                return False

        player_count -= numer_of_eyes
        player_needed -= min(4, int(numer_of_eyes / 2) * 2)

        if count_per_class_dict['archer'] % 2 != 0:
            if player_count - 1 < player_needed:
                print("One Archer missing!")
                return False

        player_count -= min(2, int(count_per_class_dict['archer'] / 2) * 2)
        player_needed -= min(2, int(count_per_class_dict['archer'] / 2) * 2)

        if count_per_class_dict['mage'] % 2 != 0:
            if player_count - 1 < player_needed:
                print("One Mage missing!")
                return False

        player_count -= count_per_class_dict['mage']
        player_needed -= int(count_per_class_dict['mage'] / 2) * 2

        if count_per_class_dict['archer'] % 2 != 0:
            if player_count - 1 < player_needed:
                print("One Archer missing!")
                return False

        player_needed -= int(count_per_class_dict['archer'] / 2) * 2 - min(2, int(count_per_class_dict['archer'] / 2) * 2)

        if player_needed > 0:
            return False

        return True

    def generate_player_lobby(self, player_lobby):
        count_per_class_dict = self.get_count_per_class_dict()

        # Priest selection

        number_of_priests = min(4 if self.m_desired_lobby_size >= 12 else 2, count_per_class_dict['priest'])

        if count_per_class_dict['priest'] >= 2:
            for i in range(number_of_priests):
                if i % 2 == 0:
                    index = self.find(lambda player: player.get_active_class() == 'priest')
                    player_lobby.m_team_left.append(self.m_available_players.pop(index))
                else:
                    index = self.find(lambda player: player.get_active_class() == 'priest')
                    player_lobby.m_team_right.append(self.m_available_players.pop(index))

        # Eye selection

        i = 0
        number_of_eyes = min(int((count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']) / 2) * 2, 4)

        for i in range(number_of_eyes):
            index = self.find(lambda player: player.get_active_class() == 'nightwalker')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        for j in range(i + 1, number_of_eyes):
            index = self.find(lambda player: player.get_active_class() == 'warrior')
            if index == len(self.m_available_players):
                break

            if j % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Archer selection

        number_of_archers = min(int((count_per_class_dict['archer']) / 2) * 2, 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.get_active_class() == 'archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Mage selection

        number_of_mages = min(int((count_per_class_dict['mage']) / 2) * 2, (int(self.m_desired_lobby_size / 2) - len(player_lobby.m_team_left)) * 2)

        for i in range(number_of_mages):
            index = self.find(lambda player: player.get_active_class() == 'mage')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Rest selection

        number_of_archers = min(int((count_per_class_dict['archer'] - number_of_archers) / 2) * 2, (int(self.m_desired_lobby_size / 2) - len(player_lobby.m_team_left)) * 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.get_active_class() == 'archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        if len(player_lobby.m_team_left + player_lobby.m_team_right) != self.m_desired_lobby_size:
            # TODO: Dump debug information
            print("Fatal Error")
