from requests.exceptions import ConnectionError as RequestsConnectionError, ReadTimeout, ChunkedEncodingError
from urllib3.exceptions import SSLError
from time import sleep
import binascii
from jukebox.lib.settings import JukeBoxSettings
from Cryptodome.Cipher import Blowfish, AES
from Cryptodome.Hash import MD5
from requests import get
from jukebox.lib.types import Services,  TrackFormats, Track

USER_AGENT_HEADER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                    "Chrome/79.0.3945.130 Safari/537.36"
def _md5(data):
    h = MD5.new()
    h.update(data.encode() if isinstance(data, str) else data)
    return h.hexdigest()

def _ecbCrypt(key, data):
    return binascii.hexlify(AES.new(key.encode(), AES.MODE_ECB).encrypt(data))

def generateBlowfishKey(trackId):
    SECRET = 'g4el58wc0zvf9na1'
    idMd5 = _md5(trackId)
    bfKey = ""
    for i in range(16):
        bfKey += chr(ord(idMd5[i]) ^ ord(idMd5[i + 16]) ^ ord(SECRET[i]))
    return bfKey

def decryptChunk(key, data):
    return Blowfish.new(key, Blowfish.MODE_CBC, b"\x00\x01\x02\x03\x04\x05\x06\x07").decrypt(data)

def generateStreamPath(sng_id, md5, media_version, media_format):
    urlPart = b'\xa4'.join(
        [md5.encode(), str(media_format).encode(), str(sng_id).encode(), str(media_version).encode()])
    md5val = _md5(urlPart)
    step2 = md5val.encode() + b'\xa4' + urlPart + b'\xa4'
    step2 = step2 + (b'.' * (16 - (len(step2) % 16)))
    urlPart = _ecbCrypt('jo6aey6haid2Teih', step2)
    return urlPart.decode("utf-8")

def generateStreamURL(sng_id, md5, media_version, media_format):
    urlPart = generateStreamPath(sng_id, md5, media_version, media_format)
    return "https://e-cdns-proxy-" + md5[0] + ".dzcdn.net/api/1/" + urlPart

def streamTrack(outputStream, track:Track, start=0):
    headers= {'User-Agent': USER_AGENT_HEADER}
    chunkLength = start
    downloadURL = generateStreamURL(track.id,track.md5,track.media_version,TrackFormats.HIFI_1411_FLAC.deezer)
    try:
        with get(downloadURL, headers=headers, stream=True, timeout=10) as request:
            request.raise_for_status()
            for chunk in request.iter_content(2048 * 3):
                outputStream.write(chunk)
                chunkLength += len(chunk)
    except (SSLError):
        streamTrack(outputStream, track, chunkLength)
    except (RequestsConnectionError, ReadTimeout, ChunkedEncodingError):
        sleep(2)
        streamTrack(outputStream, track, start)

with open('test/music.flac', 'wb') as stream:
    streamTrack(stream, 'track')