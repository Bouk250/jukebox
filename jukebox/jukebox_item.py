from aiohttp import ClientSession
from typing import Iterable, Mapping

from jukebox.lib.types import Uri, Track, StreamUrl

class JukeBoxItem:
    def __init__(self, track:Track, stream_url:StreamUrl) -> None:
        self.track = track
        self.stream_url = stream_url

        self.file_size = self.stream_url.stream_file_size
        self.progress = 0.0
        self.downloaded = 0
        
        self.canceled = False
        self.download_settings = None

        self.session:ClientSession = ClientSession()

    async def download(self):
        f = open(f'test/music/{self.track.title}{self.stream_url.stream_file_extention}', 'wb')
        with self.stream_url.stream_file_decrypter as dc:
            dc.setFileStream(f)
            async with self.session as ss:
                async with ss.get(self.stream_url.stream_url) as request:
                    async for chunk in request.content.iter_chunked(2048):
                        if self.canceled:
                            break
                        dc.decryptChunk(chunk)
                        self.update_progress(len(chunk))

    def update_progress(self, chunk_len:int):
        self.downloaded += chunk_len
        self.progress = (float(self.downloaded)/float(self.file_size))*100.0


class JukeboxItemCollection:
    
    def __init__(self):

        self.jukebox_items:Mapping[Uri, JukeBoxItem] = {}

        self.total_size = sum([item.file_size for _, item in self.jukebox_items.items()])