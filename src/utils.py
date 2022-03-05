import json
import time


def timer(function):
    def wrapper(*arg, **kwargs):
        t1 = time.time()
        function(*arg, **kwargs)
        t2 = time.time()
        print(function.__name__, 'took', t2 - t1, 's')
    return wrapper


class Data:
    def __init__(self):
        self.m_ingame_class_list = ['mage', 'archer', 'priest', 'nightwalker', 'warrior']

        with open('../data/discord_channels.json') as json_file:
            self.m_discord_channels = json.load(json_file)

        self.m_discord_command_only_channels = [self.m_discord_channels['bg-queue'], self.m_discord_channels['bot-commands']]

