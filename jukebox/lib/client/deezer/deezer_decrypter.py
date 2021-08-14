import hashlib

from binascii import a2b_hex
from Crypto.Cipher import Blowfish

from jukebox.lib.types import Track

def deezer_decrypt_file(input_data, track: Track):
    h = hashlib.md5(str(track.id).encode()).hexdigest().encode()
    key = "".join(
        chr(h[i] ^ h[i + 16] ^ b"g4el58wc0zvf9na1"[i]) for i in range(16))
    seg = 0
    for data in input_data:
        if (seg % 3) == 0 and len(data) == 2048:
            data = Blowfish.new(key.encode(), Blowfish.MODE_CBC,
                                a2b_hex("0001020304050607")).decrypt(data)
        seg += 1
        yield data