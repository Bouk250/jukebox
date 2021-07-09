from jukebox.lib.client import DeezerClient, TidalClient
from jukebox.lib.types import Track
__version__ = "Prototype - 0.0.1"

class JukeBox:
    def __init__(self):
        self.deezer_client:DeezerClient = None
        self.tidal_client:TidalClient   = None
        self.settings                   = None

    def get_track(self, **kwargs) -> Track:
        if len(kwargs.keys() & {'uri', 'url'}) != 1:
            raise ValueError('you can use uri arguments or url arguments')