import asyncio
from asyncio import queues
from jukebox.lib.status_codes import JukeBoxStatus, JukeBoxStatusCode
from jukebox.lib.types.types import StreamUrl

from typing import Tuple, Union, NoReturn, Iterable, Mapping
from aiohttp import ClientSession

from jukebox.lib.settings import ClientManagerSettings
from jukebox.lib.types import Services, Uri, FormatMap, Track
from jukebox.lib.client import DeezerClient, TidalClient

from jukebox.utils.logs import JukeBoxLogger as logger

class ServiceClientManager:

    def __init__(self, client_manager_settings:ClientManagerSettings, session:ClientSession):
        self.client_manager_settings = client_manager_settings
        self.session = session
        self.deezer_client = DeezerClient(self.client_manager_settings.deezer_settings, self.session)
        self.tidal_client = TidalClient(self.client_manager_settings.tidal_settings,self.session)

    async def login(self, service:Services, **kwargs) -> Tuple[JukeBoxStatus, int]:
        client = self.__get_client(service)
        status, user_id = await client.login(**kwargs)
        if status.status_code != JukeBoxStatusCode.Success:
            return status, None
        return JukeBoxStatus(JukeBoxStatusCode.Success), user_id

    async def load_settings(self, client_manager_settings:ClientManagerSettings) -> NoReturn:
        self.client_manager_settings = client_manager_settings
        await self.deezer_client.load_settings(self.client_manager_settings.deezer_settings)
        await self.tidal_client.load_settings(self.client_manager_settings.tidal_settings)

    async def get_tracks(self, uris:Iterable[Uri]) -> Mapping[Uri,Tuple[JukeBoxStatus,Track]]:

        uris = list(set(uris))

        work_queue = asyncio.Queue()
        for uri in uris:
            work_queue.put_nowait(uri) 
            
            
        async def get_track(name, queue:asyncio.Queue, results:dict, client_manager:ServiceClientManager) -> NoReturn:
            while True:
                # Get a "work item" out of the queue.
                uri:Uri = await queue.get()

                client = client_manager.__get_client(uri.service)
                if client.logged_in:
                    logger.info(f"[{uri.service.name} - {uri.type} - {uri.id}] Try to get track information...")
                    result = await client.api.get_track(uri)
                    if result[0].status_code != JukeBoxStatusCode.Success:
                        logger.error(f"[{uri.service.name} - {uri.type} - {uri.id}] Failed to get track information")
                    else:
                        logger.info(f"[{uri.service.name} - {uri.type} - {uri.id}] Success to get track information, Track title : {result[1].title}")
                else:
                    logger.error(f"[{uri.service.name} - {uri.type} - {uri.id}] Failed to get track information, client is not logged in")
                    result = (JukeBoxStatus(JukeBoxStatusCode.ClientNotLoggedIn), None)
                results.update({uri:result})
                # Notify the queue that the "work item" has been processed.
                queue.task_done()

        # Create three worker tasks to process the queue concurrently.
        tasks = []
        results = {}
        for i in range(min(3,work_queue.qsize())):
            task = asyncio.create_task(get_track(f'worker-{i}', work_queue, results, self))
            tasks.append(task)

        # Wait until the queue is fully processed.
        await work_queue.join()

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        
        return results

    async def get_tracks_stream_url(self, format_map:FormatMap, tracks:Iterable[Track]) -> Mapping[Uri, Tuple[JukeBoxStatus, StreamUrl]]:
        
        work_queue = asyncio.Queue()
        for track in tracks:
            work_queue.put_nowait(track)
            
        async def get_track_stream_url(name, queue:asyncio.Queue, format_map:FormatMap, results:dict, client_manager:ServiceClientManager) -> NoReturn:
            while True:
                # Get a "work item" out of the queue.
                track:Track = await queue.get()
                track_format = format_map.get(track.service)

                if track_format is None:
                    logger.error(f"[{track.service.name} - {track.title:10s}] Format map don't have format for {track.service.name} service")
                    results.update({track.uri:(JukeBoxStatus(JukeBoxStatusCode.FormatMapDontHaveTrackService, msg=f"Format map don't have format for {track.service.name} service"), None)})
                else:  

                    client = client_manager.__get_client(track.service)

                    if client.logged_in:
                        logger.info(f"[{track.service.name} - {track.artist_name} - {track.title:10s}] Try to get stream url for {track.title}, format {track_format.name}")

                        status, stream_url = await client.api.get_track_stream_url(track, track_format)

                        if status.status_code != JukeBoxStatusCode.Success:
                            results.update({track.uri:(status,None)})
                        else:
                            if stream_url.stream_track_format < track_format:
                                logger.warning(f"[{track.service.name} - {track.artist_name} - {track.title:10s}] Failed to get with {track_format.name}, get lower - {stream_url.stream_track_format.name}")
                                results.update({track.uri:(JukeBoxStatus(JukeBoxStatusCode.GotLowerAudioQuality), stream_url)})
                            elif stream_url.stream_track_format > track_format:
                                logger.warning(f"[{track.service.name} - {track.artist_name} - {track.title:10s}] Failed to get with {track_format.name}, get higher - {stream_url.stream_track_format.name}")
                                results.update({track.uri:(JukeBoxStatus(JukeBoxStatusCode.GotHigherAudioQuality), stream_url)})
                            else:
                                logger.info(f"[{track.service.name} - {track.artist_name} - {track.title:10s}] Sucsefuly get stream url with {track_format.name}")
                                results.update({track.uri:(JukeBoxStatus(JukeBoxStatusCode.Success), stream_url)})
                    else:
                        logger.error(f"[{track.service.name} - {track.artist_name} - {track.title:10s}] Failed to get track stream url, client is not logged in")
                        results.update({track.uri:(JukeBoxStatus(JukeBoxStatusCode.ClientNotLoggedIn), None)})


                queue.task_done()

        # Create three worker tasks to process the queue concurrently.
        tasks = []
        results = {}
        for i in range(min(3,work_queue.qsize())):
            task = asyncio.create_task(get_track_stream_url(f'worker-{i}', work_queue, format_map, results, self))
            tasks.append(task)

        await work_queue.join()

        for task in tasks:
            task.cancel()
        
        return results

    def __get_client(self, service:Services)-> Union[DeezerClient, TidalClient]:
        if service == Services.DEEZER:
            return self.deezer_client
        elif service == Services.TIDAL:
            return self.tidal_client
        raise KeyError