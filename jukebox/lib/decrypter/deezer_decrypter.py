from io import BufferedWriter

from Cryptodome.Cipher import Blowfish
from Cryptodome.Hash import MD5

from .decrypter import NullDecrypter
from jukebox.lib.types import Track

class DeezerDecrypter(NullDecrypter):
    def __init__(self, item: Track) -> None:
        super().__init__(item)
        self.buffer = bytes()
        self.generateBlowfishKey()       

    def _md5(self,data):
        h = MD5.new()
        h.update(data.encode() if isinstance(data, str) else data)
        return h.hexdigest()
        
    def generateBlowfishKey(self):
        SECRET = 'g4el58wc0zvf9na1'
        idMd5 = self._md5(self.item.id)
        bfKey = ""
        for i in range(16):
            bfKey += chr(ord(idMd5[i]) ^ ord(idMd5[i + 16]) ^ ord(SECRET[i]))
        self.blowfish_key = str.encode(bfKey)

    def decryptChunk(self, chunk):
        self.buffer += chunk
        if len(self.buffer) >= 2048*3:
            data = Blowfish.new(self.blowfish_key, Blowfish.MODE_CBC, b"\x00\x01\x02\x03\x04\x05\x06\x07").decrypt(self.buffer[0:2048]) + self.buffer[2048:2048*3]
            self.buffer = self.buffer[2048*3:]
            self.file_stream.write(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.buffer) >= 2048:
            data = Blowfish.new(self.blowfish_key, Blowfish.MODE_CBC, b"\x00\x01\x02\x03\x04\x05\x06\x07").decrypt(self.buffer[0:2048]) + self.buffer[2048:]
            self.file_stream.write(data)
        elif len(self.buffer) > 0:
            self.file_stream.write(self.buffer)
            
        self.close()




