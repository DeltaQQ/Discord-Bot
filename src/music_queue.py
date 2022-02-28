import queue
import _thread
import requests

from discord import FFmpegPCMAudio
from discord import PCMVolumeTransformer
from youtube_dl import YoutubeDL


class Song:
    def __init__(self, title: str, youtube_url: str, source_url_list: list, duration: int):
        self.m_title = title
        self.m_youtube_url = youtube_url
        self.m_source_url_list = source_url_list
        self.duration = duration


class MusicQueue:
    def __init__(self):
        self.m_youtube_url_queue = queue.Queue()

        ydl_options = {
            'format': 'bestaudio/best',
            'postprocessor': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'playliststart': 1,
            'playlistend': 3
        }

        self.m_youtube_dl_start = YoutubeDL(ydl_options)

        ydl_options['playliststart'] = 4
        ydl_options['playlistend'] = 100

        self.m_youtube_dl_rest = YoutubeDL(ydl_options)
        self.m_current_voice_client = None
        self.m_is_playing = False

    def set_voice_client(self, voice_client):
        self.m_current_voice_client = voice_client

    def set_volume(self, new_volume):
        self.m_current_voice_client.source = PCMVolumeTransformer(self.m_current_voice_client.source)
        self.m_current_voice_client.source.volume = new_volume

    def parse_url(self, url, youtube_dl):
        url_description = youtube_dl.extract_info('{}'.format(url), download=False)

        if '_type' in url_description and url_description['_type'] == 'playlist':
            for entry in url_description['entries']:
                title = entry['title']
                youtube_url = entry['webpage_url']

                source_url = []
                for i in range(4):
                    source_url.append(entry['formats'][i]['url'])

                duration = entry['duration']

                song_info = Song(title, youtube_url, source_url, duration)
                self.m_youtube_url_queue.put(song_info)
            return True
        else:
            title = url_description['title']
            youtube_url = url_description['webpage_url']

            source_url = []
            for i in range(4):
                source_url.append(url_description['formats'][i]['url'])

            duration = url_description['duration']

            song_info = Song(title, youtube_url, source_url, duration)
            self.m_youtube_url_queue.put(song_info)
            return False

    def submit_url(self, url):
        stripped_url = url.strip()

        if self.parse_url(stripped_url, self.m_youtube_dl_start):
            _thread.start_new_thread(self.parse_url, (stripped_url, self.m_youtube_dl_rest))

    def is_empty(self):
        return self.m_youtube_url_queue.empty()

    def clear(self):
        with self.m_youtube_url_queue.mutex:
            self.m_youtube_url_queue.queue.clear()

    def play(self):
        if self.is_empty():
            return

        if not self.m_current_voice_client:
            print('VoiceClient not initialized!')
            return

        song = self.m_youtube_url_queue.get()

        source_url_index = 4

        for url in reversed(song.m_source_url_list):
            response = requests.head(url)
            source_url_index = source_url_index - 1

            if response.ok:
                break

        if source_url_index == 0:
            print("All links are broken!")
            return

        music_source = song.m_source_url_list[source_url_index]

        self.m_current_voice_client.play(FFmpegPCMAudio(
            music_source,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
            after=lambda e: self.play()
        )

        self.set_volume(0.05)
