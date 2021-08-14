from typing import Any, Union

from abc import ABCMeta
from abc import abstractmethod

from aiohttp import ClientSession

from jukebox.lib.types import Track, TrackSchema, TrackFormats, Services, StreamUrl, Uri, Types

class API(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, session: ClientSession):
        self.session = session

    @abstractmethod
    async def get_user_data(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_track_id_from_isrc(self, track_uri: Uri) -> Uri:
        raise NotImplementedError
    @abstractmethod
    async def get_track(self, track_uri: Uri) -> Track:
        raise NotImplementedError

    @abstractmethod
    async def get_track_stream_url(self, track:Track, track_format:TrackFormats) -> StreamUrl:
        raise NotImplementedError
