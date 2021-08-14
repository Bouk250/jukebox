from abc import ABCMeta,abstractmethod
from typing import Any
from jukebox.lib.message_interface import JukeBoxMessageInterface
from  aiohttp import ClientSession

class Client(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, settings:Any, session:ClientSession):
        self.settings = settings
        self.session = session
        self.logged_in = False

    @abstractmethod
    async def load_settings(self, settings:Any):
        raise NotImplementedError

    @abstractmethod
    async def login(self, **kwargs) -> Any:
        """Login to the service"""
        raise NotImplementedError