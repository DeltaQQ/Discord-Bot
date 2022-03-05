from configparser import ConfigParser
from discord.ext import commands

from modules.dispatch_module import DispatchModule
from modules.debug_module import DebugModule
from modules.music_module import MusicModule
from modules.youtube_module import YoutubeModule
from modules.playground_module import PlaygroundModule
from modules.battleground_module import BattlegroundModule


def main():
    bot = commands.Bot(command_prefix='.', help_command=None)

    config = ConfigParser()
    config.read('../data/config.ini')

    modules = {
        'bg-queue': [BattlegroundModule(bot)],
        'pg-queue': [PlaygroundModule(bot)],
        'bot-commands': [MusicModule(bot)],
        'no-channel': [YoutubeModule(bot), DebugModule(bot)]
    }

    for channel_name in modules:
        for module in modules[channel_name]:
            bot.add_cog(module)

    bot.add_cog(DispatchModule(bot, modules))

    bot.run(config['Sensitive']['DISCORD_TOKEN'])


if __name__ == '__main__':
    main()
