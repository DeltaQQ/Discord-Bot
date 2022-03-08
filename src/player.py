import asyncio
import time

from utils import Data


class Character:
    def __init__(self, ingame_name, ingame_class, rank):
        self.m_ingame_name = ingame_name
        self.m_ingame_class = ingame_class
        self.m_rank = rank
        self.m_active = False

    def __eq__(self, other):
        if isinstance(other, Character):
            return self.m_ingame_class == other.m_ingame_class

    def active(self):
        return self.m_active


class Player(Data):
    def __init__(self, discord_id):
        super(Player, self).__init__()
        self.m_id = discord_id
        self.m_in_queue = False
        self.m_queue_join_time = 0
        self.m_characters = []

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.m_id == other.m_id

    def get_active_class(self):
        for character in self.m_characters:
            if character.active():
                return character.m_ingame_class

    def get_active_rank(self):
        for character in self.m_characters:
            if character.active():
                return character.m_rank

    def add_characters(self, player_library, *args):
        for i in range(len(args)):
            if i % 2 == 0:
                if args[i + 1].lower() in self.m_ingame_class_list:
                    rank = player_library.get_rank(self.m_id, args[i + 1].lower(), args[i])
                    self.m_characters.append(Character(args[i], args[i + 1].lower(), rank))
                else:
                    print("Invalid class argument(s)")
                    raise Exception

    def remove_character(self, character):
        self.m_characters.remove(character)

    async def expired(self, player_queue, channel):
        await asyncio.sleep(3600)

        if (time.time() - self.m_queue_join_time) >= 3600:
            if player_queue.find(lambda p: p.m_id == self.m_id) != player_queue.size():
                player_queue.remove_player(lambda p: p.m_id == self.m_id)
                await channel.purge(check=lambda m: m.author.id == self.m_id)
