from jukebox.lib.status_codes.jukebox_status_codes import JukeBoxStatus, JukeBoxStatusCode
import time
import asyncio
from typing import Tuple

from aiohttp import ClientSession

from ..client import Client
from .tidal_api import TidalAPI

from jukebox.utils.logs import JukeBoxLogger as logger
from jukebox.lib.settings import TidalSetings

from pprint import pprint

class TidalClient(Client):

    def __init__(self, settings: TidalSetings, session: ClientSession):
        self.settings = settings
        self.session = session
        self.api = TidalAPI(self.session, self.settings)
        self.logged_in = False

    async def login(self) -> Tuple[JukeBoxStatus, int]:
        logger.info('[TidalClient] - Try to login...')
        status, result = await self.api.get_device_code()
        if status.status_code != JukeBoxStatusCode.Success:
            logger.error(f'[TidalClient] Tidal login failed, error: {status.msg}')
            self.logged_in = False
            return status, None
        
        pprint(result)

        self.settings.key.device_code = result['deviceCode']
        self.settings.key.user_code = result['userCode']
        self.settings.key.verification_url = result['verificationUri']
        self.settings.key.expires_in = result['expiresIn']
        self.settings.key.auth_check_interval = result['interval']
        
        start = time.time()
        elapsed = 0
        while elapsed < self.settings.key.expires_in:
            elapsed = time.time() - start
            status, result = await self.api.check_auth_status(self.settings.key.device_code)

            if status.status_code == JukeBoxStatusCode.TidalAuthorizationCheckStatus and status.msg == 'Pending':
                logger.info("[TidalClient] Pending")
                await asyncio.sleep(self.settings.key.auth_check_interval + 1)
                
            elif status.status_code != JukeBoxStatusCode.Success:
                logger.error('[TidalClient] Tidal login failed')
                self.logged_in = False
                return status, None

            else:
                self.settings.user_id = result['user']['userId']
                self.settings.key.country_code = result['user']['countryCode']
                self.settings.key.access_token = result['access_token']
                self.settings.key.refresh_token = result['refresh_token']
                self.settings.key.expires_in = result['expires_in']

                self.session.headers.update({'authorization': f'Bearer {self.settings.key.access_token}'})

                logger.info('[TidalClient] Successful login')
                self.logged_in = True
                return JukeBoxStatus(JukeBoxStatusCode.Success), self.settings.user_id

        if elapsed >= self.settings.key.expires_in:
            self.logged_in = False
            return JukeBoxStatus(JukeBoxStatusCode.TidalAuthorizationCheckTimeout), None

    async def load_settings(self, settings: TidalSetings):
        self.settings = settings
        self.api.tidal_settings = self.settings
        self.logged_in = False
        logger.info('[TidalClient] Try to login...')
        status = await self.api.verify_access_token()
        if status.status_code != JukeBoxStatusCode.Success:
            logger.error('[TidalClient] Login failed')
        else:
            self.session.headers.update({'authorization': f'Bearer {self.settings.key.access_token}'})
            self.logged_in = True
            logger.info('[TidalClient] Successful login')

            