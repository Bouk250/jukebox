import json
import mimetypes
from typing import Tuple, Union
from pprint import pprint
from aiohttp import ClientSession, ClientTimeout
from urllib.parse import urljoin

from jukebox.lib.types import Track, TrackSchema, TrackFormats, Services, StreamUrl, Uri, Types
from jukebox.lib.client.api import API
from jukebox.lib.status_codes.jukebox_status_codes import JukeBoxStatus, JukeBoxStatusCode
from jukebox.lib.decrypter import DeezerDecrypter

from jukebox.utils.logs import JukeBoxLogger as logger


DEEZER_GWAPI_URL = "http://www.deezer.com/ajax/gw-light.php"
DEEZER_API_URL = "https://api.deezer.com/"


class DeezerAPI(API):

    def __init__(self, session: ClientSession):
        self.session = session
        self.api_token = None
        self.license_token = None

    async def __api_post_request(self, method: str = None, args: dict = {}, params: dict = {}, url: str = DEEZER_GWAPI_URL) -> Tuple[JukeBoxStatus, dict]:

        if method:
            if method == 'deezer.getUserData':
                api_token = 'null'
            else:
                if self.api_token is None:
                    await self.get_user_data()
                api_token = self.api_token

            params.update({
                'api_version': "1.0",
                'api_token': api_token,
                'input': '3',
                'method': method})
        else:
            method = url

        post_kwargs = {
            'url': url,
            'params': params,
            'json': args,
        }

        logger.debug(f"[DeezerAPI] Try to call '{method}' method...")

        try:
            async with self.session.post(**post_kwargs) as req:
                result = await req.json()

        except Exception as e:
            logger.error(f"[DeezerAPI] API request error: {str(e)}")
            return JukeBoxStatus(JukeBoxStatusCode.ApiRequestError, str(e)), None

        if 'error' in result.keys() and len(result['error']):
            logger.error(f"[DeezerAPI] API method '{method}' error: {json.dumps(result['error'])}")
            return JukeBoxStatus(JukeBoxStatusCode.DeezerApiError, json.dumps(result['error'])), None

        logger.debug(f"[DeezerAPI] Method '{method}' called with success")
        return JukeBoxStatus(JukeBoxStatusCode.Success), result

    async def __api_get_request(self, url: str = DEEZER_API_URL, method: str = None) -> Tuple[JukeBoxStatus, dict]:

        if method:
            url = urljoin(url, method)
        else:
            method = url

        get_kwargs = {
            'url': url
        }

        logger.debug(f"[DeezerAPI] Try to call '{method}' method...")

        try:
            async with self.session.get(**get_kwargs) as req:
                result_json = await req.json()

        except Exception as e:
            logger.error(f"[DeezerAPI] API request error: {str(e)}")
            return JukeBoxStatus(JukeBoxStatusCode.ApiRequestError, str(e)), None

        if 'error' in result_json.keys():
            logger.error(
                f"[DeezerAPI] API error: {json.dumps(result_json['error'])}")
            return JukeBoxStatus(JukeBoxStatusCode.DeezerApiError, json.dumps(result_json['error'])), None

        logger.debug(f"[DeezerAPI] Method '{method}' called with success")
        return JukeBoxStatus(JukeBoxStatusCode.Success), result_json

    async def get_user_data(self) -> Tuple[JukeBoxStatus, dict]:
        status, result = await self.__api_post_request(method='deezer.getUserData')
        result = result['results']
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        self.api_token = result['checkForm']
        self.license_token = result['USER']['OPTIONS']['license_token']
        return JukeBoxStatus(JukeBoxStatusCode.Success), result

    async def get_track_id_from_isrc(self, track_uri: Uri) -> Tuple[JukeBoxStatus, Uri]:

        new_track_uri = Uri(Services.DEEZER, Types.TRACK, "")

        status, result = await self.__api_get_request(method=f'track/isrc:{track_uri.id}')
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None

        new_track_uri.id = result['id']
        return JukeBoxStatus(JukeBoxStatusCode.Success), new_track_uri

    async def get_track(self, track_uri: Uri) -> Tuple[JukeBoxStatus, Track]:
        if track_uri.type == Types.ISRC:
            status, temp_uri = await self.get_track_id_from_isrc(track_uri)
            if status.status_code != JukeBoxStatusCode.Success:
                return status, None
        else:
            temp_uri = track_uri

        if temp_uri.service != Services.DEEZER:
            return JukeBoxStatus(JukeBoxStatusCode.UriServiceNotCompatible, msg=f"Track service is {temp_uri.service.value} and api service is deezer"), None

        song_id = temp_uri.id
        status, result = await self.__api_post_request(method='song.getListData', args={"sng_ids": [song_id]})
        result = result['results']
        if result['count'] == 0:
            return JukeBoxStatus(JukeBoxStatusCode.DeezerApiDataNotFound), None

        
        data = result['data'][0].copy()
        data.update({'service':Services.DEEZER.value})
        #pprint(data)
        schema = TrackSchema()
        
        track = schema.load(data=data)
        track.uri = track_uri.copy()

        return JukeBoxStatus(JukeBoxStatusCode.Success), track

    async def get_track_stream_url(self, track: Track, track_format: TrackFormats) -> Tuple[JukeBoxStatus, StreamUrl]:

        if track.service != Services.DEEZER:
            return JukeBoxStatus(JukeBoxStatusCode.UriServiceNotCompatible, msg=f"Track service is {track.service.value} and api service is deezer"), None

        formats = []

        for format_iteam in TrackFormats.get_service_formats(track.service):
            if format_iteam <= track_format:
                formats.append(
                    {'cipher': 'BF_CBC_STRIPE', 'format': format_iteam.services[track.service]['service_format']})
        args = {
            'license_token': self.license_token,
            'media': [{"type": "FULL", "formats": formats}, ],
            'track_tokens': [track.track_token],
        }

        status, result = await self.__api_post_request(url="https://media.deezer.com/v1/get_url", args=args)
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None
        
        url = result['data'][0]['media'][0]['sources'][0]['url']
        url_format = result['data'][0]['media'][0]['format']
        url_track_file_format = TrackFormats.get_format_from_name(track.service, url_format)

        extention = url_track_file_format.services.get(Services.DEEZER).get('extentions').get(url_format)
        
        async with self.session.head(url) as head:
            file_size = head.content_length

        stream_url = StreamUrl(stream_track_format=url_track_file_format,
                               stream_file_size=file_size, stream_url=url,
                               stream_file_decrypter=DeezerDecrypter(track),
                               stream_file_extention=extention)

        return JukeBoxStatus(JukeBoxStatusCode.Success), stream_url
