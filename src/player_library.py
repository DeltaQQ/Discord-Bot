import json

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

