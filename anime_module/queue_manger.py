from .m3u8 import M3U8

from async_io import requests
from modules import Thread

from asyncio import gather, new_event_loop, sleep, Queue
from copy import deepcopy
from time import sleep as b_sleep
from typing import Optional

from uuid import uuid1

class VideoQueue:
    def __init__(self, thread_num: int) -> None:
        """
        下載排程器。

        thread_num: :class:`int`
            同時下載數量。
        """
        # 資料表
        self._downloader_dict: dict[str, M3U8] = {}
        # 順序清單
        self._queue_list = []
        # 下載中清單
        self._download_list = []
        # 同時下載數量
        self._thread_num = thread_num

        self.__uuid = uuid1().hex[:8]
        
        Thread(target=self._thread_job, name=f"VideoQueue-{self.__uuid}").start()
    
    def _thread_job(self):
        loop = new_event_loop()
        self._coro_list = []
        for _ in range(self._thread_num):
            self._coro_list.append(
                loop.create_task(self._manage_job(), name=f"VQ-{self.__uuid} Manger")
            )
        
        loop.run_until_complete(gather(*self._coro_list, return_exceptions=True))
    
    async def _manage_job(self):
        while True:
            # 檢查是否有空閒中的任務
            if len(self._queue_list) <= len(self._download_list):
                await sleep(1)
                continue
            # 取得新任務
            for _downloader_id in self._queue_list:
                if _downloader_id not in self._download_list:
                    break
            _downloader = self._downloader_dict.get(_downloader_id)
            if _downloader == None:
                self._download_list.remove(_downloader_id)
                continue
            self._download_list.append(_downloader_id)

            # 開始下載
            await _downloader.download()

            # 下載後清除
            self._download_end(_downloader_id)
            self._download_list.remove(_downloader_id)
    
    def _download_end(self, _downloader_id: str):
        _downloader = self._downloader_dict[_downloader_id]
        # 如果下載完成
        if _downloader.finish:
            self._queue_list.remove(_downloader_id)
            Thread(target=self._delete_job, args=(_downloader_id,)).start()
    
    def _after_update(self):
        _should_run = self._queue_list[:self._thread_num]
        for _running in self._download_list:
            if _running in _should_run: continue
            _downloader = self._downloader_dict[_running]
            _downloader.stop()
    
    def _delete_job(self, downloader_id: str):
        b_sleep(60)
        del self._downloader_dict[downloader_id]

    def add(self, downloader: M3U8) -> None:
        """
        新增下載排程。

        downloader: :class:`M3U8`
            下載器。
        """
        _downloader_id = f"u-{uuid1().hex}"
        _downloader = downloader

        self._downloader_dict[_downloader_id] = _downloader
        self._queue_list.append(_downloader_id)
    
    def remove(self, downloader_id: str) -> None:
        """
        移除下載排程。

        downloader_id: :class:`str`
            下載器ID。
        """
        _downloader = self._downloader_dict.get(downloader_id)
        if _downloader == None: return
        # 尚未開始
        if _downloader.status_code() == 4:
            del self._downloader_dict[downloader_id]
            return

        # 正在下載中
        if _downloader.started:
            _downloader.stop(True)
            return

        # 被中斷
        if not _downloader.finish:
            _downloader.stop(True)
        self._download_end(downloader_id)
    
    def update(self, queue_list: list[str]) -> None:
        """
        更新順序清單。

        queue_list: :class:`list[str]`
            順序清單。
        """
        _old_queue_list = deepcopy(self._queue_list)
        _new_queue_list = []
        for _downloader_id in queue_list:
            try:
                _old_queue_list.remove(_downloader_id)
                _new_queue_list.append(_downloader_id)
            except ValueError: continue
        _new_queue_list += _old_queue_list
        self._queue_list = _new_queue_list
        self._after_update()
    
    def get_queue(self) -> list[str]:
        """
        取得排程。
        """
        return deepcopy(self._queue_list)
    
    def get_downloader(self, downloader_id: str) -> Optional[M3U8]:
        """
        取得下載器。

        downloader_id: :class:`str`
            下載器ID。
        """
        return self._downloader_dict.get(downloader_id)
    
    def upper(self, downloader_id: str):
        """
        將排程向上提一位。

        downloader_id: :class:`str`
            下載器ID。
        """
        try: _index = self._queue_list.index(downloader_id)
        except ValueError: return
        if _index == 0: return

        self._queue_list[_index], self._queue_list[_index-1] = self._queue_list[_index-1], self._queue_list[_index]

        self._after_update()
    
    def lower(self, downloader_id: str):
        """
        將排程向下提一位。

        downloader_id: :class:`str`
            下載器ID。
        """
        try: _index = self._queue_list.index(downloader_id)
        except ValueError: return
        if _index == len(self._queue_list) - 1: return

        self._queue_list[_index], self._queue_list[_index+1] = self._queue_list[_index+1], self._queue_list[_index]

        self._after_update()

class ImageCacheQueue:
    def __init__(self, connect_num: int) -> None:
        """
        下載排程器。

        connect_num: :class:`int`
            同時連接數量。
        """
        self.__uuid = uuid1().hex[:8]
        self._connect_num = connect_num
        self._image_queue = Queue()
        
        Thread(target=self._thread_job, name=f"ImageCacheQueue-{self.__uuid}").start()
    
    def _thread_job(self):
        loop = new_event_loop()
        self._coro_list = []
        for _ in range(self._connect_num):
            self._coro_list.append(
                loop.create_task(self._downloader(), name=f"ICQ-{self.__uuid} Downloader")
            )
        
        loop.run_until_complete(gather(*self._coro_list, return_exceptions=True))
    
    async def add(self, url: str):
        await self._image_queue.put(url)
    
    def add_nowait(self, url: str):
        self._image_queue.put_nowait(url)
    
    async def _downloader(self):
        while True:
            # 檢查是否有空閒中的任務
            if self._image_queue.empty():
                await sleep(1)
                continue
            # 取得新任務
            _url = await self._image_queue.get()
            # 開始下載
            try:
                await requests(_url, from_cache=True)
            except:
                await self._image_queue.put(_url)
