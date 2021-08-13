from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import asyncio
import aiohttp
import logging

from aiohttp import ClientSession

from codetiming import Timer
from pprint import pprint

from jukebox import JukeBoxUser, JukeBox
from jukebox.lib.types import Services, Uri, Types, FormatMap, TrackFormats
from jukebox.lib.settings import JukeBoxUserSettings
from jukebox.lib.status_codes.jukebox_status_codes import JukeBoxStatusCode

from jukebox.utils.logs import JukeBoxLogger as logger
from jukebox.utils.analyser import UrisGenerater

#logger.setLevel(logging.DEBUG)

async def main():
    async with JukeBox() as jb:
        settings = JukeBoxUserSettings.load("test/user_settings.yaml")

        async with JukeBoxUser() as user:
            await user.load_settings(settings)
            #await user.login(Services.TIDAL)
            uris = UrisGenerater(["https://listen.tidal.com/track/184786799", 'https://www.deezer.com/fr/track/1283264142', 'deezer:isrc:USAT22100017', 'https://tidal.com/browse/track/188267445', 'https://tidal.com/track/191046575'])
            tracks = await user.get_tracks(uris)
            tracks_list = []
            for k, (status, track) in tracks.items():
                if status.status_code == JukeBoxStatusCode.Success:
                    tracks_list.append(track)
            
            fm = FormatMap()
            fm.set(Services.DEEZER, TrackFormats.LOSSY_256)
            fm.set(Services.TIDAL, TrackFormats.LOSSY_256)

            results = await user.get_tracks_stream_url(fm,tracks_list)
            
            async with aiohttp.ClientSession() as session:
                for k, (status, stream_url) in results.items():
                    print(f"{str(k)} {stream_url.stream_track_format.name} {stream_url.stream_file_extention} {stream_url.stream_url}", end="\n\n")
                    f = open(f'test/music/{tracks[k][1].title}{stream_url.stream_file_extention}', 'wb')
                    with stream_url.stream_file_decrypter as dc:
                        dc.setFileStream(f)
                        async with session.get(stream_url.stream_url) as request:
                            async for chunk in request.content.iter_chunked(2048):
                                dc.decryptChunk(chunk)
            
    #settings.save("test/user_settings.yaml")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())