import asyncio
import time


class Player:
    def __init__(self, discord_id, name, ingame_name, ingame_class, rank, alternative_classes):
        self.m_discord_id = discord_id
        self.m_name = name
        self.m_ingame_name = ingame_name
        self.m_ingame_class = ingame_class
        self.m_alternative_classes = alternative_classes
        self.m_rank = rank
        self.m_in_queue = False
        self.m_queue_join_time = 0

    def __eq__(self, other):
        if isinstance(other, str):
            return self.m_name == other

        if isinstance(other, Player):
            return self.m_name == other.m_name

    async def expired(self, player_queue, channel):
        await asyncio.sleep(3600)

        if (time.time() - self.m_queue_join_time) >= 3600:
            if player_queue.find(lambda p: p.m_name == self.m_name) != player_queue.size():
                player_queue.remove_player(lambda p: p.m_name == self.m_name)
                await channel.purge(check=lambda m: m.author.id == self.m_discord_id)
