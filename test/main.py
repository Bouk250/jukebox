from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import asyncio
import aiohttp
import logging

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
        #settings.client_manager_settings.deezer_settings.arl = "7c01f336c2c3d7d25235d39ffa1a4d95dc9cdd92210f9a3c8e7b9e2028d779bab1a20242d46223b8e65b83dc1330725e61b04350705312949a4e25d6cc4f0150aa0fc308caba8d2dd1af1a5b58bfc36e2a6e92193139e7d854b655ae163c0673"

        #settings.save("test/user_settings.yaml")
        #settings.client_manager_settings.tidal_settings.key.access_token = "eyJraWQiOiI4UUhqclVzdSIsImFsZyI6IlJTMjU2In0.eyJ0eXBlIjoibzJfYWNjZXNzIiwidWlkIjoxNzM1MTE1MjcsInNjb3BlIjoid19zdWIgcl91c3Igd191c3IiLCJnVmVyIjowLCJzVmVyIjoyLCJjaWQiOjMwMDYsImV4cCI6MTYyNzIxODQ4OCwic2lkIjoiMjVmMGM0MTgtOWExNy00MjczLWE2MTMtOWQxZTFmMzE2MWJiIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLnRpZGFsLmNvbS92MSJ9.LOkbT6DBy4YE3Zqu1--dx0V3SPwEo4MebSq0rX-LmpWGmWhJ61oMjYTsYUDcng03kvhhutbHQY9bOtR0xyrODldAV2BgU-cdjBuGqnVQcWpZfsiGk9UhrWEmGO46WPYbi01ZMsq0_3gitAvp-Yh1PYnvZx0pB4ZrUEUdzpUbuv8yKBljb_b-tG4erKeiIRVQbcNO0LYSeIqPHydvR-ZmH_nbs1x-_9rrqAZEQOtPYvDYyPyvgQHVlHPpE1AETlJP3K0219gzBkDjtUQcEyId-ainD0HYhUy4z3l2km1DYtH9EmG_GppjK8sAAWXlEFKYhlAvAURo__30ot8PQEQWMA"
        #settings.client_manager_settings.tidal_settings.country_code = 'IL'

        async with JukeBoxUser() as user:
            await user.load_settings(settings)
            #await user.login(Services.TIDAL)
            uris = UrisGenerater(["https://listen.tidal.com/track/184786799", 'https://www.deezer.com/fr/track/1283264142', 'deezer:isrc:USAT22100017', 'https://tidal.com/browse/track/188267445', 'https://tidal.com/track/191046575'])
            results = await user.get_tracks(uris)

            tracks = []
            for k, (status, track) in results.items():
                if status.status_code == JukeBoxStatusCode.Success:
                    tracks.append(track)
            
            fm = FormatMap()
            fm.set(Services.DEEZER, TrackFormats.HI_FI)
            fm.set(Services.TIDAL, TrackFormats.HI_RES)

            results = await user.get_tracks_stream_url(fm,tracks)
            for k, (status, stream_url) in results.items():
                print(f"{str(k)} {stream_url.stream_track_format.name} {stream_url.stream_url}", end="\n\n")
                

            """
            sng_id = [
                437046332,
                1409072752,
            ]
            uris = [Uri(Services.DEEZER,Types.TRACK,id) for id in sng_id]
            uris.append(Uri(Services.DEEZER, Types.ISRC, "USAT22100017"))
            uris.append('https://www.deezer.com/fr/track/1283264142')
            
            #with Timer(text="\nTotal elapsed time: {:.1f}"):
            tracks = await user.get_tracks(*uris)
            fm = FormatMap()
            fm.set(Services.DEEZER, TrackFormats.HIFI_1411_FLAC)
            await user.update_tracks_stream_url(fm,*tracks)

            jb_iteams = user.generate_download_items(*tracks)

            jb.add_download_items_to_queue(*jb_iteams)
            jb.start()
            print("Start to download")
            await asyncio.sleep(5)
            sng_id = [
                1370066842,
                1390823292,
            ]
            uris = [Uri(Services.DEEZER,Types.TRACK,id) for id in sng_id]
            
            #with Timer(text="\nTotal elapsed time: {:.1f}"):
            tracks = await user.get_tracks(*uris)
            fm = FormatMap()
            fm.set(Services.DEEZER, TrackFormats.LOSSY_320_MP3)
            await user.update_tracks_stream_url(fm,*tracks)

            jb_iteams = user.generate_download_items(*tracks)
            jb.add_download_items_to_queue(*jb_iteams)
            """
    #settings.save("test/user_settings.yaml")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())