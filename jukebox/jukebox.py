import asyncio
from typing import List

from jukebox.lib.types import Types, Track, Services
from jukebox.lib.client import DeezerClient, TidalClient
from jukebox.lib.exceptions import JukeBoxServiceNotLoggedException
from jukebox.lib.settings import JukeBoxSettings
from jukebox.lib.downloader import JukeBoxDownloader

from jukebox.utils.analyser import url_uri_analizer
from jukebox.utils.logs import JukeBoxLogger as logger

__version__ = "Prototype - 0.0.2"


class JukeBox:
    def __init__(self, settings:JukeBoxSettings=None):
        """
        JukeBox is a lib for download song from multiple streaming service
        """
        self.settings = JukeBoxSettings() if settings is None else settings
        self.clients = {
            Services.DEEZER: DeezerClient(self.settings.deezer_settings),
            Services.TIDAL : TidalClient(self.settings.tidal_settings), 
        }
        self.downloader = JukeBoxDownloader(self.settings)        

    @property
    def login_status(self):
        status = {
            Services.DEEZER: self.clients[Services.DEEZER].logged_in,
            Services.TIDAL: self.clients[Services.TIDAL].logged_in,
        }
        return status

    async def login(self, service:Services, **kwargs):
        if service == Services.NOT_RECOGNIZED:
            raise ValueError()
        if service == Services.DEEZER:
            arl = kwargs.get('arl')
            if arl == None:
                raise ValueError()
            try:
                await self.clients[service].login(arl=arl)
            except Exception as e:
                print(str(e))
        elif service == Services.TIDAL:
            try:
                self.clients[service].login()
            except Exception as e:
                logger.error(str(e))
    
    async def get_tracks(self, *args) -> List[Track]:
        """
        get_track retunr Track object from url or uri.
        """

        uris = []
        for arg in args:
            uri = url_uri_analizer(arg)
            if uri and uri not in uris:
                uris.append(uri)
                
        tracks = []
        for uri in uris:
            if uri.type != Types.TRACK and uri.type != Types.ISRC:
                raise ValueError()
            if not self.login_status[uri.service]:
                raise JukeBoxServiceNotLoggedException(f"Service {uri.service.value} is not logged")
            track = await self.clients[uri.service].api.get_track(uri)
            tracks.append(track)
        
        return tracks

    def get_stream_url(self, *args):
        pass
    
    def download_track(self, track: Track):
        pass