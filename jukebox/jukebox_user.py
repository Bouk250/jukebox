
from jukebox.lib.types.types import StreamUrl
from jukebox.lib.status_codes.jukebox_status_codes import JukeBoxStatus
from typing import Iterable, NoReturn, Tuple, Union
from aiohttp import ClientSession, ClientTimeout

from jukebox.lib.types import Services, Uri, Track, FormatMap
from jukebox.lib.settings import JukeBoxUserSettings
from jukebox.lib.client import ServiceClientManager
from jukebox.lib.downloader import JukeBoxItem

API_CALL_TIMEOUT = ClientTimeout(total=30)

class JukeBoxUser:

    def __init__(self):
        self.user_settings = JukeBoxUserSettings()

        self.http_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/79.0.3945.130 Safari/537.36",
            "Accept-Language": self.user_settings.accept_language,
        }

        self.session = ClientSession(headers=self.http_headers, timeout=API_CALL_TIMEOUT)

        self.client_manager = ServiceClientManager(self.user_settings.client_manager_settings, self.session)
    
    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc, tb) -> None:
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
    
    @property
    def uuid(self):
        return self.user_settings.uuid

    async def load_settings(self, user_settings:JukeBoxUserSettings) -> NoReturn:
        self.user_settings = user_settings
        await self.client_manager.load_settings(self.user_settings.client_manager_settings)
   
    def generate_download_items(self, *args:Union[Track]) -> list:
        items = []
        for item in args:
            if type(item) is Track:
                download_items = JukeBoxItem()
                download_items.items.append(item)
                items.append(download_items)
        
        return items

    async def close(self):
        await self.session.close()

    async def login(self, service:Services, **kwargs):
        await self.client_manager.login(service, **kwargs)

    async def get_tracks(self, uris:Iterable[Union[str,Uri]]) -> Iterable[Tuple[JukeBoxStatus,Track]]:
        return await self.client_manager.get_tracks(uris)

    async def get_tracks_stream_url(self, format_map:FormatMap, tracks:Iterable[Track]) -> Iterable[Tuple[JukeBoxStatus, Track, StreamUrl]]:
        return await self.client_manager.get_tracks_stream_url(format_map, tracks)