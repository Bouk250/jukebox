from jukebox.lib.types import Track
from jukebox import JukeBox
from jukebox.lib.types import Services,  TrackFormats
from pprint import pprint
from jukebox.utils.logs import JukeBoxLogger as logger
import logging
from dataclasses import asdict
from jukebox.lib.client.deezer.deezer_decrypter import deezer_decrypt_file
import asyncio


logger.setLevel(logging.DEBUG)

jb = JukeBox()

async def main():
    pprint(asdict(jb.settings))
    await jb.login(Services.DEEZER, arl = '7c01f336c2c3d7d25235d39ffa1a4d95dc9cdd92210f9a3c8e7b9e2028d779bab1a20242d46223b8e65b83dc1330725e61b04350705312949a4e25d6cc4f0150aa0fc308caba8d2dd1af1a5b58bfc36e2a6e92193139e7d854b655ae163c0673')
    logger.debug(jb.login_status)

    tracks = jb.get_tracks("https://www.deezer.com/fr/track/437046332","deezer:track:90305559", "deezer:isrc:USAT22100017")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


"""
#pprint(asdict(jb.settings))
#jb.login(Services.TIDAL)
#logger.debug(jb.login_status)

#pprint(asdict(jb.settings))
#track = jb.get_track(url='https://tidal.com/browse/track/190237715')

print(tracks)
for track in tracks:
    jb.clients[track.service].api.get_track_stream_url(track, TrackFormats.HIFI_1411_FLAC)
    print(track.title)
    current = 0
    with open(f'test/{track.title}.flac',"wb") as f:
        with requests.get(track.stream_urls[0].stream_url, stream=True) as crypt:
            for data in deezer_decrypt_file(crypt.iter_content(2048), track):
                current += len(data)
                print(current)
                f.write(data)
"""