from player_queue import PlayerQueue


class BattlegroundQueue(PlayerQueue):
    def __init__(self):
        super(BattlegroundQueue, self).__init__()

    def ready_for_matching(self):
        count_per_class_dict = self.get_count_per_class_dict()

        player_count = self.size()

        if player_count < 10:
            print("Not enough players available!")
            return

        if count_per_class_dict['priest'] == 1 and player_count - 1 < 10:
            print("One Priest missing!")
            return False

        if (count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']) % 2 != 0:
            if player_count - 1 < 10:
                print("One Eye missing!")
                return False

        if count_per_class_dict['archer'] % 2 != 0:
            if player_count - 1 < 10:
                print("One Archer missing!")
                return False

        if count_per_class_dict['mage'] % 2 != 0:
            if player_count - 1 < 10:
                print("One Mage missing!")
                return False

        return True

    def generate_player_lobby(self, player_lobby):
        if self.size() < 10:
            print("Not enough players available!")
            return

        count_per_class_dict = self.get_count_per_class_dict()

        # Priest selection

        if count_per_class_dict['priest'] == 2:
            index = self.find(lambda player: player.m_ingame_class == 'priest')
            player_lobby.m_team_left.append(self.m_available_players.pop(index))

            index = self.find(lambda player: player.m_ingame_class == 'priest')
            player_lobby.m_team_right.append(self.m_available_players.pop(index))

        # Eye selection

        i = 0
        number_of_eyes = min(int((count_per_class_dict['nightwalker'] + count_per_class_dict['warrior']) / 2) * 2, 4)

        for i in range(number_of_eyes):
            index = self.find(lambda player: player.m_ingame_class == 'nightwalker')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        for j in range(i + 1, number_of_eyes):
            index = self.find(lambda player: player.m_ingame_class == 'warrior')
            if index == len(self.m_available_players):
                break

            if j % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Archer selection

        number_of_archers = min(int((count_per_class_dict['archer']) / 2) * 2, 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Mage selection

        number_of_mages = min(int((count_per_class_dict['mage']) / 2) * 2, (5 - len(player_lobby.m_team_left)) * 2)

        for i in range(number_of_mages):
            index = self.find(lambda player: player.m_ingame_class == 'mage')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Rest selection

        number_of_archers = min(int((count_per_class_dict['archer'] - number_of_archers) / 2) * 2, (5 - len(player_lobby.m_team_left)) * 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        if len(player_lobby.m_team_left + player_lobby.m_team_right) != 10:
            # TODO: Dump debug information
            print("Fatal Error")
