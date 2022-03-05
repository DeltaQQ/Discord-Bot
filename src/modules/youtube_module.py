import asyncio
from discord.ext import commands

from src.youtube_manager import YoutubeManager
from src.utils import Data


class YoutubeModule(commands.Cog, name='youtube-module'):
    def __init__(self, bot):
        self.bot = bot
        self.m_data = Data()
        self.m_youtube_manager = YoutubeManager()

    async def send_message_to_channel(self, channel_id, message):
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)

    async def on_update(self):
        first_post = True

        while True:
            if self.m_youtube_manager.channel_is_live('Cover'):
                if first_post:
                    print("Cover is live!")
                    url = self.m_youtube_manager.current_stream_url
                    message = self.m_youtube_manager.m_youtube_channels['Cover']['message'] + "\n" + str(url)
                    channel_id = self.m_data.m_discord_channels['cover-live']

                    await self.send_message_to_channel(channel_id, message)
                    first_post = False
            else:
                first_post = True

            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Successfully logged in as {self.bot.user}")
        self.bot.loop.create_task(self.on_update())
