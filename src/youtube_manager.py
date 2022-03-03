import json
import requests

from bs4 import BeautifulSoup


class YoutubeManager:
    def __init__(self):
        self.m_youtube_channels = {}
        self.load_youtube_channels()

        self.current_stream_url = {}

    def load_youtube_channels(self):
        with open('../data/youtube_channels.json') as json_file:
            self.m_youtube_channels = json.load(json_file)

    def channel_is_live(self, user):
        channel_url = "https://www.youtube.com/channel/{}/live".format(self.m_youtube_channels[user]['channelID'])
        destination = requests.get(channel_url, cookies={'CONSENT': 'YES+42'})
        soup = BeautifulSoup(destination.content, 'html.parser')
        live = soup.find('link', {'rel': 'canonical'})

        if 'watch?v' in live.get('href'):
            self.current_stream_url = live.get('href')
            return True

        return False
