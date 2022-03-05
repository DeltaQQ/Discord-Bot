from discord.ext import commands

from src.utils import Data


class DispatchModule(commands.Cog, name='dispatch-module'):
    # Modules is a hash table with the module reference as key
    # and the related discord channel as value
    def __init__(self, bot, modules):
        self.bot = bot
        self.m_data = Data()
        self.m_modules = modules

    @commands.command(name='join')
    async def join(self, ctx, *args):
        for channel_name in self.m_modules:
            if ctx.channel.id == self.m_data.m_discord_channels[channel_name]:
                for module in self.m_modules[channel_name]:
                    await module.join(ctx, *args)

    @commands.command(name='leave')
    async def leave(self, ctx):
        for channel_name in self.m_modules:
            if ctx.channel.id == self.m_data.m_discord_channels[channel_name]:
                for module in self.m_modules[channel_name]:
                    await module.leave(ctx)
