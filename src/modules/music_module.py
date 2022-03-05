from discord.ext import commands
from discord.utils import get

from src.utils import Data
from src.music_queue import MusicQueue


class MusicModule(commands.Cog, name='music-module'):
    def __init__(self, bot):
        self.bot = bot
        self.m_data = Data()
        self.m_music_queue = MusicQueue()

    async def join(self, ctx, *args):
        if self.is_connected_to_channel(ctx):
            await ctx.voice_client.disconnect()

        channel = ctx.message.author.voice.channel
        await channel.connect()

        self.m_music_queue.set_voice_client(get(ctx.bot.voice_clients, guild=ctx.guild))

    async def leave(self, ctx):
        if not self.is_connected_to_channel(ctx):
            return

        await ctx.voice_client.disconnect()

    @commands.command(name='submit')
    async def submit(self, ctx, url):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return

        self.m_music_queue.submit_url(url)

    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return

        voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

        if not voice_client.is_playing():
            return

        voice_client.pause()

    @commands.command(name='play')
    async def play(self, ctx):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return

        voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client.is_playing():
            print("Already playing!")
            return

        self.m_music_queue.play()

    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return

        voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client.is_paused():
            voice_client.resume()

    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return
        voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
        voice_client.stop()

    @commands.command(name='clear')
    async def clear(self, ctx):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return

        self.m_music_queue.clear()

    @commands.command(name='loop')
    async def loop(self, ctx, url, repeat_count):
        if ctx.channel.id != self.m_data.m_discord_channels['bot-commands']:
            return

        for i in range(int(repeat_count)):
            self.m_music_queue.submit_url(url)

    @staticmethod
    def is_connected_to_channel(ctx):
        voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()
