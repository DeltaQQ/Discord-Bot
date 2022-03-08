from utils import Data

from player import Player


class PlayerQueue(Data):
    def __init__(self):
        super().__init__()

        self.m_available_players = []

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
            for character in player.m_characters:
                if character.active():
                    count_per_class_dict[character.m_ingame_class] += 1

        return count_per_class_dict
