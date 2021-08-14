from io import BufferedWriter

from jukebox.lib.types import Track

class NullDecrypter:
    def __init__(self, item:Track) -> None:
        self.item = item
    
    def setFileStream(self, file_stream:BufferedWriter):
        self.file_stream = file_stream

    def decryptChunk(self, chunk):
        self.file_stream.write(chunk)

    def close(self):
        self.file_stream.close()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):            
        self.close()