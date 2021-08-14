from typing import NoReturn, Tuple
from jukebox.lib.status_codes.jukebox_status_codes import JukeBoxStatus, JukeBoxStatusCode
from  aiohttp import ClientSession
from http.cookies import Morsel

from .deezer_api import DeezerAPI
from ..client import Client

from jukebox.lib.settings import DeezerSetings

from jukebox.utils.logs import JukeBoxLogger as logger

class DeezerClient(Client):

    def __init__(self, settings:DeezerSetings, session:ClientSession):
        self.settings = settings

        self.session = session
        
        self.api = DeezerAPI(self.session)
        self.logged_in = False

    async def load_settings(self, settings:DeezerSetings) -> NoReturn:
        self.settings = settings
        logger.info('[DeezerClient] Settings successfully loaded')
        if self.settings.arl and self.settings.arl != '':
            status, _ = await self.login(self.settings.arl)
            if status.status_code != JukeBoxStatusCode.Success:
                logger.warning('[DeezerClient] AutoLogin failed, login with new arl')


    async def login(self, arl:str) -> Tuple[JukeBoxStatus, int]:
        logger.info('[DeezerClient] Try to login...')
        
        arl = arl.strip()

        cookie = Morsel()
        cookie.set('arl', arl, arl)
        cookie['path'] = '/'
        cookie['domain'] = 'deezer.com'
        cookie['httponly'] = True
        
        cookies = {
            'arl':cookie
        }

        self.session.cookie_jar.update_cookies(cookies=cookies)

        status, result = await self.api.get_user_data()
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        # Check if user logged in
        user_id = result["USER"]["USER_ID"]
        if user_id == 0:
            self.logged_in = False
            logger.error('[DeezerClient] Login via arl failed')
            return JukeBoxStatus(JukeBoxStatusCode.DeezerLoginFaile), None

        logger.info('[DeezerClient] Successful login')
        self.logged_in = True
        self.settings.arl = arl
                
        return JukeBoxStatus(JukeBoxStatusCode.Success), user_id
