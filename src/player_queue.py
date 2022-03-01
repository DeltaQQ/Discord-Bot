from utils import Data


class Player:
    def __init__(self, discord_id, name, ingame_name, ingame_class, rank):
        self.m_discord_id = discord_id
        self.m_name = name
        self.m_ingame_name = ingame_name
        self.m_ingame_class = ingame_class
        self.m_rank = rank

    def __eq__(self, other):
        if isinstance(other, str):
            return self.m_name == other

        if isinstance(other, Player):
            return self.m_name == other.m_name


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

    def already_in_queue(self, name):
        for player in self.m_available_players:
            if name in player.m_name:
                return True

        return False

    def add_player(self, discord_id, name, ingame_name, ingame_class, rank):
        player = Player(discord_id, name, ingame_name, ingame_class, rank)
        self.m_available_players.append(player)

    def remove_player(self, condition):
        index = self.find(condition)
        self.m_available_players.pop(index)

    def get_count_per_class_dict(self):
        count_per_class_dict = {x: 0 for x in self.m_ingame_class_list}

        for player in self.m_available_players:
            count_per_class_dict[player.m_ingame_class] += 1

        return count_per_class_dict

    def ready_for_matching(self):
        count_per_class_dict = self.get_count_per_class_dict()

        player_count = self.size()

        if player_count < 10:
            print("Not enough players available!")
            return

        if count_per_class_dict['Priest'] == 1 and player_count - 1 < 10:
            print("One Priest missing!")
            return False

        if (count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']) % 2 != 0:
            if player_count - 1 < 10:
                print("One Eye missing!")
                return False

        if count_per_class_dict['Archer'] % 2 != 0:
            if player_count - 1 < 10:
                print("One Archer missing!")
                return False

        if count_per_class_dict['Mage'] % 2 != 0:
            if player_count - 1 < 10:
                print("One Archer missing!")
                return False

        return True

    def generate_player_lobby(self, player_lobby):
        if self.size() < 10:
            print("Not enough players available!")
            return

        count_per_class_dict = self.get_count_per_class_dict()

        # Priest selection

        if count_per_class_dict['Priest'] == 2:
            index = self.find(lambda player: player.m_ingame_class == 'Priest')
            player_lobby.m_team_left.append(self.m_available_players.pop(index))

            index = self.find(lambda player: player.m_ingame_class == 'Priest')
            player_lobby.m_team_right.append(self.m_available_players.pop(index))

        # Eye selection

        i = 0
        number_of_eyes = min(int((count_per_class_dict['Nightwalker'] + count_per_class_dict['Warrior']) / 2) * 2, 4)

        for i in range(number_of_eyes):
            index = self.find(lambda player: player.m_ingame_class == 'Nightwalker')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        for j in range(i + 1, number_of_eyes):
            index = self.find(lambda player: player.m_ingame_class == 'Warrior')
            if index == len(self.m_available_players):
                break

            if j % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Archer selection

        number_of_archers = min(int((count_per_class_dict['Archer']) / 2) * 2, 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'Archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Mage selection

        number_of_mages = min(int((count_per_class_dict['Mage']) / 2) * 2, (5 - len(player_lobby.m_team_left)) * 2)

        for i in range(number_of_mages):
            index = self.find(lambda player: player.m_ingame_class == 'Mage')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        # Rest selection

        number_of_archers = min(int((count_per_class_dict['Archer'] - number_of_archers) / 2) * 2, (5 - len(player_lobby.m_team_left)) * 2)

        for i in range(number_of_archers):
            index = self.find(lambda player: player.m_ingame_class == 'Archer')
            if index == len(self.m_available_players):
                break

            if i % 2 == 0:
                player_lobby.m_team_right.append(self.m_available_players.pop(index))
            else:
                player_lobby.m_team_left.append(self.m_available_players.pop(index))

        if len(player_lobby.m_team_left + player_lobby.m_team_right) != 10:
            # TODO: Dump debug information
            print("Fatal Error")
