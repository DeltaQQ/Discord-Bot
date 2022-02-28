import json
import requests

from googleapiclient.discovery import build
from bs4 import BeautifulSoup


class YoutubeManager:
    def __init__(self, api_key):
        self.m_api_service_name = "youtube"
        self.m_api_version = "v3"
        self.m_youtube_service = build(self.m_api_service_name, self.m_api_version, developerKey=api_key)
        self.m_response = {}
        self.m_something_was_requested = False

        self.m_youtube_channels = {}
        self.load_youtube_channels()

        self.current_stream_url = {}

    def user_is_live(self, user):
        request = self.m_youtube_service.search().list(
            part='snippet',
            channelId=self.m_youtube_channels[user]['channelID'],
            eventType='live',
            type='video'
        )

        self.m_response = request.execute()
        self.m_something_was_requested = True

        result_string = json.dumps(self.m_response['items'])
        if result_string == '[]':
            return False

        result_string = json.dumps(self.m_response['items'][0]['snippet']['liveBroadcastContent'])
        if result_string == '"live"':
            return True

    def get_current_response(self):
        if not self.m_something_was_requested:
            print("No API request made so far")
            return

        return self.m_response

    def save_response_to_file(self, filename='response.json'):
        if self.m_something_was_requested:
            output_file = open(filename, 'w')
            json.dump(self.m_response, output_file, indent=4)
            output_file.close()
        else:
            print("No API request made so far")
            return

    def load_youtube_channels(self):
        with open('youtube_channels.json') as json_file:
            self.m_youtube_channels = json.load(json_file)

    def print_live_users(self):
        for user in self.m_youtube_channels:
            if self.user_is_live(user):
                print(user, "is live!")

    def extract_url_from_response(self):
        return [f"https://www.youtube.com/watch?v={video['id']['videoId']}" for video in self.m_response['items']]

    def channel_is_live(self, user):
        channel_url = "https://www.youtube.com/channel/{}/live".format(self.m_youtube_channels[user]['channelID'])
        destination = requests.get(channel_url, cookies={'CONSENT': 'YES+42'})
        soup = BeautifulSoup(destination.content, 'html.parser')
        live = soup.find('link', {'rel': 'canonical'})

        if 'watch?v' in live.get('href'):
            self.current_stream_url = live.get('href')
            return True

        return False

    def shutdown(self):
        self.m_youtube_service.close()
