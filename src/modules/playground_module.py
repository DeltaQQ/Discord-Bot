from discord.ext import commands


class PlaygroundModule(commands.Cog, name='playground-module'):
    def __init__(self, bot):
        self.bot = bot
