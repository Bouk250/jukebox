from __future__ import annotations
import aiohttp
import asyncio


from jukebox.lib.settings import JukeBoxSettings
from jukebox.lib.downloader import JukeBoxItem

from jukebox.lib.decrypter import NullDecrypter

__version__ = "Prototype - 0.0.2"


class JukeBox:

    def __init__(self, settings:JukeBoxSettings=None):
        """
        JukeBox is a lib for download song from multiple streaming service
        """
        self.work_queue:asyncio.Queue = asyncio.Queue()
        self.tasks = []

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self):
        return self

    def add_download_items_to_queue(self, *args:JukeBoxItem):
        for item in args:
            self.work_queue.put_nowait(item)

    """
    def start(self):
        async def downloader(name, queue:asyncio.Queue):
            async with aiohttp.ClientSession() as session:
                while True:

                    jb_item:JukeBoxItem = await queue.get()

                    for item in jb_item.items:
                        f = open(f'test/music/{item.title}{item.stream_urls[0].stream_track_format.file_format}', 'wb')
                        with Decrypter(item,f) as dc:
                            async with session.get(item.stream_urls[0].stream_url) as request:
                                async for chunk in request.content.iter_chunked(2048):
                                    dc.decryptChunk(chunk)
                    queue.task_done()

        for i in range(5):
            task = asyncio.create_task(downloader(f'worker-{i}', self.work_queue))
            self.tasks.append(task)
    """
    async def close(self):

        await self.work_queue.join()
        # Cancel our worker tasks.
        for task in self.tasks:
            task.cancel()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()