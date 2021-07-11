from typing import List
import eventlet
from jukebox.lib.types.types import Types
from jukebox.lib.client import DeezerClient, TidalClient
from jukebox.lib.types import Track, Services
from jukebox.utils.analyser import url_analizer
from jukebox.lib.exceptions import JukeBoxServiceNotLoggedException
from jukebox.utils.logs import JukeBoxLogger as logger
from jukebox.lib.settings import JukeBoxSettings

__version__ = "Prototype - 0.0.2"
urlopen = eventlet.import_patched('urllib.request').urlopen

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
        

    @property
    def login_status(self):
        status = {
            Services.DEEZER: self.clients[Services.DEEZER].logged_in,
            Services.TIDAL: self.clients[Services.TIDAL].logged_in,
        }
        return status

    def login(self, service:Services, **kwargs):
        if service == Services.NOT_RECOGNIZED:
            raise ValueError()
        if service == Services.DEEZER:
            arl = kwargs.get('arl')
            if arl == None:
                raise ValueError()
            try:
                self.clients[service].login(arl=arl)
            except:
                pass
        elif service == Services.TIDAL:
            try:
                self.clients[service].login()
            except Exception as e:
                logger.error(str(e))
    
    def get_tracks(self, **kwargs) -> List[Track]:
        """
        get_track retunr Track object from url or uri.
        """
        #TODO Suport multi url
        if len(kwargs.keys() & {'uri', 'url', 'isrc'}) != 1:
            raise ValueError('you can use uri arguments or url or isrc arguments')
        url = kwargs.get('url')
        uri = kwargs.get('uri')
        isrc = kwargs.get('isrc')

        if isrc is not None:
            id = f'isrc:{isrc}'
            tracks = []
            for service, client in self.clients.items():
                if self.login_status[service]:
                    tracks.append(self.clients[service].api.get_track(id))

        elif  url is not None:
            if 'deezer.page.link' in url: url = urlopen(url).url
            service, url_type, id = url_analizer(url=url)
            if url_type != Types.TRACK:
                raise ValueError()

        if service != Services.NOT_RECOGNIZED and not self.login_status[service]:
            raise JukeBoxServiceNotLoggedException(f"Service {service.value} is not logged")

        return [self.clients[service].api.get_track(id)]

    def download_track(self, track: Track):
        pass