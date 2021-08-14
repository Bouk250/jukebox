import base64
import ast

from jukebox.lib.status_codes.jukebox_status_codes import JukeBoxStatusCode
from pprint import pprint
from typing import Union, Iterable, Tuple
from jukebox.lib.status_codes import JukeBoxStatus
from urllib.parse import urljoin
from aiohttp import ClientSession, BasicAuth

from ..api import API

from jukebox.lib.settings import TidalSetings
from jukebox.lib.types import Track, TrackFormats, Uri, StreamUrl, Types, TrackSchema, Services
from jukebox.lib.decrypter import NullDecrypter

from jukebox.utils.logs import JukeBoxLogger as logger

TIDAL_URL_PRE = 'https://api.tidalhifi.com/v1/'
TIDAL_AUTH_URL = 'https://auth.tidal.com/v1/oauth2/'
# known API key for Fire Stick HD(MQA, Dolby Vision enabled)
TIDAL_API_KEY = {'clientId': 'aR7gUaTK1ihpXOEP',
                 'clientSecret': 'eVWBEkuL2FCjxgjOkR3yK0RYZEbcrMXRc2l8fU3ZCdE='}


class TidalAPI(API):

    def __init__(self, session: ClientSession, tidal_settings: TidalSetings):
        self.session = session
        self.tidal_settings = tidal_settings

    async def __api_get_request(self, method: str = None, params: dict = {}, url: str = TIDAL_URL_PRE) -> Tuple[JukeBoxStatus, dict]:

        if method:
            url = urljoin(url, method)
        else:
            method = url

        params.update({'countryCode': self.tidal_settings.key.country_code})

        get_kwargs = {
            'url': url,
            'params': params,
        }

        logger.debug(f"[TidalAPI] Try to call '{method}' method...")

        try:
            async with self.session.get(**get_kwargs) as req:
                result = await req.json()

        except Exception as e:
            logger.error(f"[TidalAPI] API request error: {str(e)}")
            return JukeBoxStatus(JukeBoxStatusCode.ApiRequestError, msg=str(e)), None

        logger.debug(f"[TidalAPI] Method '{method}' called with success")
        return JukeBoxStatus(JukeBoxStatusCode.Success), result

    async def __api_post_request(self, method: str = None, data: dict = {}, auth: BasicAuth = None, url: str = TIDAL_AUTH_URL) -> Tuple[JukeBoxStatus, dict]:

        if method:
            url = urljoin(url, method)
        else:
            method = url

        post_kwargs = {
            'url': url,
            'data': data,
            'auth': auth,
        }

        logger.debug(f"[TidalAPI] Try to call '{method}' method...")

        try:
            async with self.session.post(**post_kwargs) as req:
                result = await req.json()
        except Exception as e:
            logger.error(f"[TidalAPI] API request error: {str(e)}")
            return JukeBoxStatus(JukeBoxStatusCode.ApiRequestError, msg=str(e)), None

        logger.debug(f"[TidalAPI] Method '{method}' called with success")
        return JukeBoxStatus(JukeBoxStatusCode.Success), result

    async def get_device_code(self) -> Tuple[JukeBoxStatus, dict]:
        data = {
            'client_id': TIDAL_API_KEY['clientId'],
            'scope': 'r_usr+w_usr+w_sub'
        }
        status, result = await self.__api_post_request(method='device_authorization', data=data)
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        if 'status' in result and result['status'] != 200:
            return JukeBoxStatus(JukeBoxStatusCode.TidalDeviceAuthorizationFailed, msg="Device authorization failed. Please try again."), None

        return JukeBoxStatus(JukeBoxStatusCode.Success), result

    async def check_auth_status(self, device_code: str) -> Tuple[JukeBoxStatus, dict]:
        data = {
            'client_id': TIDAL_API_KEY['clientId'],
            'device_code': device_code,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'scope': 'r_usr+w_usr+w_sub'
        }
        auth = BasicAuth(
            TIDAL_API_KEY['clientId'], TIDAL_API_KEY['clientSecret'], encoding='utf-8')

        status, result = await self.__api_post_request(method='token', data=data, auth=auth)
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        if 'status' in result and result['status'] != 200:
            if result['status'] == 400 and result['sub_status'] == 1002:
                return JukeBoxStatus(JukeBoxStatusCode.TidalAuthorizationCheckStatus, msg="Pending"), None

            else:
                return JukeBoxStatus(JukeBoxStatusCode.TidalAuthorizationCheckStatus, msg="Error while checking for authorization. Trying again..."), None

        return JukeBoxStatus(JukeBoxStatusCode.Success), result

    async def verify_access_token(self) -> JukeBoxStatus:

        header = {'Authorization': f'Bearer {self.tidal_settings.key.access_token}'}

        get_kwargs = {
            'url': 'https://api.tidal.com/v1/sessions',
            'headers': header,
        }
        try:
            async with self.session.get(**get_kwargs) as req:
                result = await req.json()
        except Exception as e:
            return JukeBoxStatus(JukeBoxStatusCode.ApiRequestError, msg=str(e))
        if 'status' in result.keys() and result['status'] != 200:
            return JukeBoxStatus(JukeBoxStatusCode.TidalApiError, msg=result)
        return JukeBoxStatus(JukeBoxStatusCode.Success)

    async def get_track(self, track_uri: Uri) -> Tuple[JukeBoxStatus, Track]:
        if track_uri.type == Types.ISRC:
            track_uri = await self.get_track_id_from_isrc(track_uri)

        song_id = track_uri.id

        status, result = await self.__api_get_request(method=f"tracks/{song_id}")
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        # pprint(result)

        data = result.copy()
        data.update({'service': Services.TIDAL.value})

        schema = TrackSchema()

        track = schema.load(data=data)
        track.uri = track_uri.copy()

        return JukeBoxStatus(JukeBoxStatusCode.Success), track

    async def get_track_id_from_isrc(self, track_uri: Uri) -> Uri:
        pass

    async def get_track_stream_url(self, track: Track, track_format: TrackFormats) -> Tuple[JukeBoxStatus, StreamUrl]:
        sound_param = track_format.services.get(Services.TIDAL)

        params = {"audioquality": sound_param.get('service_format'),
                  "playbackmode": "STREAM", "assetpresentation": "FULL"}

        status, result = await self.__api_get_request(method=f"tracks/{track.id}/playbackinfopostpaywall", params=params)
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        track_format = TrackFormats.get_format_from_name(
            Services.TIDAL, result.get('audioQuality'))
        manifest = result.get('manifest')

        manifest = base64.urlsafe_b64decode(manifest)
        manifest = ast.literal_eval(str(manifest, "utf-8"))

        extention = sound_param.get('extentions').get(manifest.get('mimeType'))

        encryption = manifest.get('encryptionType')
        decrypter = NullDecrypter(track)
        if encryption != 'NONE':
            pass

        url = manifest.get('urls')[0]

        async with self.session.head(url) as head:
            file_size = head.content_length

        return JukeBoxStatus(JukeBoxStatusCode.Success), StreamUrl(track_format, stream_file_size=file_size, 
                                                                    stream_url=url, stream_file_decrypter=decrypter, 
                                                                    stream_file_extention=extention)

    async def get_user_data(self) -> dict:
        pass
