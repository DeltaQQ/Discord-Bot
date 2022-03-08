from player_queue import PlayerQueue


class PlaygroundQueue(PlayerQueue):
    def __init__(self):
        super(PlaygroundQueue, self).__init__()

    def ready_for_matching(self):
        pass

    def generate_player_lobby(self, player_lobby):
        pass
