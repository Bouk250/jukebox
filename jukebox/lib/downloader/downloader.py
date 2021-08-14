
import grequests

class JukeBoxDownloader:

    def __init__(self, settings:dict):
        self.settings = settings
    
    def start(self):
        raise NotImplementedError