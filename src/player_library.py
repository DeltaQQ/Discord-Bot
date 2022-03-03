import json
import operator
import os
import sys

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

    def add_player(self, name):
        start_entry = {x: 1000 for x in self.m_ingame_class_list}
        self.m_player_library[name] = start_entry

    def update_player(self, name, ingame_class, entry):
        self.m_player_library[name][ingame_class] = entry

    def remove_player(self, name):
        del self.m_player_library[name]

    def get_rank(self, name, ingame_class):
        if name not in self.m_player_library:
            self.add_player(name)

        return self.m_player_library[name][ingame_class]

    def update_ranking(self, filename):
        list_everyone = []

        for player in self.m_player_library:
            for ingame_class in self.m_player_library[player]:
                rank = self.get_rank(player, ingame_class)
                if rank != 1000.0:
                    list_everyone.append((player, ingame_class, int(rank)))

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
