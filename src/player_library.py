import json
import operator
import os
import sys
from copy import deepcopy

from utils import Data


class PlayerLibrary(Data):
    def __init__(self):
        super().__init__()

        self.m_player_library = {}
        self.m_filename = ""
        self.m_library_loaded = False

    def load(self, filename):
        with open(filename) as player_library:
            self.m_player_library = json.load(player_library)

            self.m_library_loaded = True
            self.m_filename = filename

    def persist(self):
        if not self.m_library_loaded:
            print("Player Library not loaded!")
            return

        with open(self.m_filename, 'w') as player_library:
            json.dump(self.m_player_library, player_library, indent=4)

    def add_player(self, discord_id, ingame_class, ingame_name):
        self.m_player_library[str(discord_id)] = {ingame_class: {'rank': 1000, 'name': ingame_name}}

        remaining_class_list = deepcopy(self.m_ingame_class_list)
        remaining_class_list.remove(ingame_class)

        for ingame_class in remaining_class_list:
            self.m_player_library[str(discord_id)][ingame_class] = {'rank': 1000, 'name': 'none'}

    def update_player(self, discord_id, ingame_class, ingame_name):
        self.m_player_library[str(discord_id)][ingame_class]['name'] = ingame_name

    def remove_player(self, discord_id):
        del self.m_player_library[str(discord_id)]

    def get_rank(self, discord_id, ingame_class, ingame_name='none'):
        if str(discord_id) not in self.m_player_library:
            self.add_player(discord_id, ingame_class, ingame_name)
        else:
            self.update_player(discord_id, ingame_class, ingame_name)

        self.persist()

        return self.m_player_library[str(discord_id)][ingame_class]['rank']

    def get_name(self, discord_id, ingame_class):
        return self.m_player_library[str(discord_id)][ingame_class]['name']

    def update_ranking(self, filename):
        list_everyone = []

        for player in self.m_player_library:
            for ingame_class in self.m_player_library[player]:
                rank = self.m_player_library[player][ingame_class]['rank']
                name = self.m_player_library[player][ingame_class]['name']
                if rank != 1000.0:
                    list_everyone.append((name, ingame_class, int(rank)))

        list_everyone.sort(key=operator.itemgetter(2), reverse=True)

        end_index = min(len(list_everyone), 50)

        player_ranking = {}

        for i in range(end_index):
            player_ranking[i + 1] = [list_everyone[i][0], list_everyone[i][1].capitalize(), list_everyone[i][2]]

        with open(filename, 'w') as json_file:
            json_file.flush()
            json.dump(player_ranking, json_file, indent=4)

        if sys.platform == "linux" or sys.platform == "linux2":
            os.system('sudo cp ../data/player_ranking.json /var/www/html/')
