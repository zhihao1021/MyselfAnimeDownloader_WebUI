from .m3u8 import M3U8

from asyncio import CancelledError, create_task, current_task, gather, Queue, sleep, Task

from uuid import uuid1

class VideoQueue:
    def __init__(self, thread: int) -> None:
        """
        下載排程器。

        thread: :class:`int`
            同時下載數量。
        """
        self._thread_list = []
    
    def 

    def add(self, downloader: M3U8) -> None:
        pass