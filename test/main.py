from marshmallow import schema
from jukebox import JukeBox
from jukebox.lib.types import Services,  TrackFormats, TrackSchema
from pprint import pprint
from jukebox.utils.logs import JukeBoxLogger as logger
import logging
from dataclasses import asdict
from jukebox.lib.client.deezer.deezer_stream_url import get_stream_url
from ssl import SSLError
from time import sleep
import logging
from Crypto.Cipher import AES, Blowfish
import hashlib
from binascii import a2b_hex, b2a_hex

logger.setLevel(logging.DEBUG)

jb = JukeBox()

pprint(asdict(jb.settings))
jb.login(Services.DEEZER, arl = '7c01f336c2c3d7d25235d39ffa1a4d95dc9cdd92210f9a3c8e7b9e2028d779bab1a20242d46223b8e65b83dc1330725e61b04350705312949a4e25d6cc4f0150aa0fc308caba8d2dd1af1a5b58bfc36e2a6e92193139e7d854b655ae163c0673')
logger.debug(jb.login_status)

#pprint(asdict(jb.settings))
#jb.login(Services.TIDAL)
#logger.debug(jb.login_status)

#pprint(asdict(jb.settings))
#track = jb.get_track(url='https://tidal.com/browse/track/190237715')
track = jb.get_tracks(url="https://deezer.page.link/5uCEGzpkt5JzQHjGA")[0]


url = jb.clients[Services.DEEZER].api.get_track_stream_url(track, TrackFormats.LOSSY_256_MP3)
#print(generateStreamURL(track.id, track.md5, track.media_version, TrackFormats.HIFI_1411_FLAC))

def md5hex(data: bytes) -> bytes:
    return hashlib.md5(data).hexdigest().encode()

def decrypt_file(input_data, track_id: int):

    h = md5hex(str(track_id).encode())
    key = "".join(
        chr(h[i] ^ h[i + 16] ^ b"g4el58wc0zvf9na1"[i]) for i in range(16))
    seg = 0
    for data in input_data:
        if (seg % 3) == 0 and len(data) == 2048:
            data = Blowfish.new(key.encode(), Blowfish.MODE_CBC,
                                a2b_hex("0001020304050607")).decrypt(data)
        seg += 1
        yield data

pprint(asdict(track))
"""
crypt = jb.clients[Services.DEEZER].api.session.get(url, stream=True)
current = 0
with open('test/test.flac',"wb") as f:
    for data in decrypt_file(crypt.iter_content(2048), track.id):
        current += len(data)
        f.write(data)
"""