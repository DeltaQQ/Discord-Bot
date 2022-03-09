from discord.ext import commands

from src.utils import Data


class DebugModule(commands.Cog, name='debug-module'):
    def __init__(self, bot):
        self.bot = bot
        self.m_data = Data()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id in self.m_data.m_discord_command_only_channels:
            if not message.content.startswith('.') or message.content.startswith('. '):
                await message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        channel = args[0].channel
        await channel.purge(limit=1, check=lambda m: m.author.id == args[0].author.id)

    @commands.command(name='purge')
    async def purge(self, ctx):
        if ctx.author.top_role.name != 'Admin' and ctx.author.id != 339770100628455424:
            return

        await ctx.channel.purge()
