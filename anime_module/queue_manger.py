from .m3u8 import M3U8

from aiorequests import requests
from configs import GLOBAL_CONFIG
from utils import Thread

from asyncio import all_tasks, new_event_loop, sleep, Queue
from copy import deepcopy
from time import sleep as b_sleep
from typing import Optional

from uuid import uuid1

class VideoQueue:
    def __init__(self, thread_num: Optional[int]=None) -> None:
        """
        下載排程器。

        :param thread_num: :class:`int`同時下載數量。
        """
        # 資料表
        self.__downloader_dict: dict[str, M3U8] = {}
        # 順序清單
        self.__queue_list = []
        # 下載中清單
        self.__download_list = []
        # 同時下載數量
        self.__thread_num = GLOBAL_CONFIG.worker if thread_num == None else thread_num

        self.loop = new_event_loop()
        for _ in range(self.__thread_num):
            self.loop.create_task(self.__manage_job(), name=f"VQ-{self.__uuid} Manger")

        # ID
        self.__uuid = uuid1().hex[:8]
        
        Thread(target=self.__thread_job, name=f"VideoQueue-{self.__uuid}").start()
    
    def __thread_job(self):
        try:
            self.loop.run_forever()
        except SystemExit:
            for task in all_tasks(self.loop):
                task.cancel()
            self.loop.stop()
    
    async def __manage_job(self):
        while True:
            # 檢查是否有空閒中的任務
            queue_list = tuple(filter(lambda did: did not in self.__download_list, self.__queue_list))
            if len(queue_list) == 0:
                await sleep(1)
                continue
            # 取得新任務
            downloader_id = queue_list[0]
            
            # 檢查下載器是否為空
            downloader = self.__downloader_dict.get(downloader_id)
            if downloader == None:
                self.__queue_list.remove(downloader_id)
                continue

            # 新增至下載中
            self.__download_list.append(downloader_id)

            # 開始下載
            await downloader.download()

            # 下載後清除
            self.__download_list.remove(downloader_id)
            if downloader.finish:
                self.__queue_list.remove(downloader_id)
                self.loop.create_task(self.__delete_job(downloader_id))
    
    async def __delete_job(self, downloader_id: str):
        """
        等待60秒後移除下載器。
        """
        await b_sleep(60)
        del self.__downloader_dict[downloader_id]

    def __after_update(self):
        """
        貯列更新後，對下載器狀態進行變更。
        """
        should_run = self.__queue_list[:self.__thread_num]
        for running in filter(lambda did: did not in should_run, self.__download_list):
            downloader = self.__downloader_dict[running]
            downloader.stop()

    def add(self, downloader: M3U8) -> None:
        """
        新增下載排程。

        :param downloader: :class:`M3U8`下載器。
        """
        downloader_id = f"u-{uuid1().hex}"
        downloader = downloader

        self.__downloader_dict[downloader_id] = downloader
        self.__queue_list.append(downloader_id)
    
    def remove(self, downloader_id: str) -> None:
        """
        移除下載排程。

        :param downloader_id: :class:`str`下載器ID。
        """
        downloader = self.__downloader_dict.get(downloader_id)
        if downloader == None:
            return
        # 尚未開始
        if downloader.status_code() == 4:
            pass
        # 正在下載中
        if downloader.started:
            downloader.stop(True)
            return
        # 被中斷
        if not downloader.finish:
            downloader.stop(True)

        # 清除
        self.__queue_list.remove(downloader_id)
        del self.__downloader_dict[downloader_id]
    
    def update(self, queue_list: list[str]) -> None:
        """
        更新順序清單。

        :param queue_list: :class:`list[str]`順序清單。
        """
        new_queue_list = []
        # 尋找存在的ID
        for downloader_id in filter(lambda did: did in self.__queue_list, queue_list):
            new_queue_list.append(downloader_id)
        # 新增未被移動的ID
        new_queue_list += list(filter(lambda did: did not in self.__queue_list, queue_list))
        self.__queue_list = new_queue_list
        self.__after_update()
    
    def get_queue(self) -> list[str]:
        """
        取得排程。
        """
        return deepcopy(self.__queue_list)
    
    def get_downloader(self, downloader_id: str) -> Optional[M3U8]:
        """
        取得下載器。

        :param downloader_id: :class:`str`下載器ID。
        """
        return self.__downloader_dict.get(downloader_id)
    
    def upper(self, downloader_id: str):
        """
        將排程向上提一位。

        :param downloader_id: :class:`str`下載器ID。
        """
        try:
            index = self.__queue_list.index(downloader_id)
        except ValueError:
            return
        if index == 0:
            return

        self.__queue_list[index], self.__queue_list[index-1] = self.__queue_list[index-1], self.__queue_list[index]

        self.__after_update()
    
    def lower(self, downloader_id: str):
        """
        將排程向下移一位。

        :param downloader_id: :class:`str`下載器ID。
        """
        try:
            index = self.__queue_list.index(downloader_id)
        except ValueError:
            return
        if index == len(self.__queue_list) - 1:
            return

        self.__queue_list[index], self.__queue_list[index+1] = self.__queue_list[index+1], self.__queue_list[index]

        self.__after_update()

class ImageCacheQueue:
    def __init__(self, connect_num: int) -> None:
        """
        下載排程器。

        :param connect_num: :class:`int`同時連接數量。
        """
        self.__uuid = uuid1().hex[:8]
        self.__image_queue = Queue()

        self.loop = new_event_loop()
        for _ in range(connect_num):
            self.loop.create_task(self.__downloader)
        
        Thread(target=self.__thread_job, name=f"ImageCacheQueue-{self.__uuid}").start()
    
    def __thread_job(self):
        try:
            self.loop.run_forever()
        except SystemExit:
            for task in all_tasks(self.loop):
                task.cancel()
            self.loop.stop()
    
    async def add(self, url: str):
        await self.__image_queue.put(url)
    
    def add_nowait(self, url: str):
        self.__image_queue.put_nowait(url)
    
    async def __downloader(self):
        while True:
            # 檢查是否有空閒中的任務
            if self.__image_queue.empty():
                await sleep(0.1)
                continue
            # 取得新任務
            _url = await self.__image_queue.get()
            # 開始下載
            try:
                await requests(_url, from_cache=True, raise_exception=True)
            except:
                await self.__image_queue.put(_url)
