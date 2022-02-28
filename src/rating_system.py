from player_queue import Player
from player_library import PlayerLibrary


# https://en.wikipedia.org/wiki/Elo_rating_system for reference


def update_rating(player_library: PlayerLibrary, winner: list[Player], loser: list[Player]):
    r_winner = 0
    for player in winner:
        r_winner += player.m_rank

    r_winner = r_winner / 5

    r_loser = 0
    for player in loser:
        r_loser += player.m_rank

    r_loser = r_loser / 5

    e_winner = 1 / (1 + 10**((r_loser - r_winner) / 400))
    e_loser = 1 / (1 + 10**((r_winner - r_loser) / 400))

    k = 16
    if (r_winner + r_loser) / 2 <= 2000:
        k = 32

    for player in winner:
        r_winner_new = player_library.m_player_library[player.m_name][player.m_ingame_class] + k * (1 - e_winner)
        player_library.update_player(player.m_name, player.m_ingame_class, r_winner_new)

    for player in loser:
        r_loser_new = player_library.m_player_library[player.m_name][player.m_ingame_class] + k * (0 - e_loser)
        player_library.update_player(player.m_name, player.m_ingame_class, r_loser_new)

    player_library.persist()
