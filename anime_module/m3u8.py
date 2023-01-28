from aiorequests import new_session, requests
from configs import FFMPEG_ARGS, GLOBAL_CONFIG, TIMEZONE
from utils import retouch_path

from asyncio import CancelledError, create_task, current_task, gather, get_running_loop, Queue, sleep, Task
from datetime import datetime
from logging import getLogger
from os import makedirs, rename, rmdir, stat, walk
from os.path import abspath, join, isfile, isdir, split
from shutil import rmtree
from subprocess import run, DEVNULL, PIPE
from traceback import format_exception
from typing import Optional
from urllib.parse import urljoin, urlparse

from aiofiles import open as aopen
from aiohttp import ClientSession


def recursion_delete_dir(dir_path: str):
    delete_num = 0
    for path, folder, file in walk(dir_path, topdown=False):
        if folder == [] and file == []:
            try:
                rmdir(path)
                delete_num += 1
            except:
                pass
    if delete_num:
        recursion_delete_dir(dir_path)


class M3U8:
    def __init__(self,
                 host: str,
                 m3u8_file: str,
                 output_name: str,
                 output_dir: Optional[str] = None,
                 ) -> None:
        """
        M3U8下載器。

        :param host: :class:`str`主機位置。
        :param m3u8_file: :class:`str`.m3u8文件位置。
        :param output_name: :class:`str`輸出檔案名稱。
        :param output_dir: :class:`str`輸出資料夾位置。
        """
        # 主機位置
        self.host = host if host.endswith("/") else (host + "/")
        # 檔案位置
        self.m3u8_file = m3u8_file

        # 輸出檔名
        self.output_name = output_name
        # 輸出資料夾
        self.output_dir = "download" if output_dir == None else abspath(
            output_dir)
        # 暫存資料夾
        self.temp_dir = abspath(join(
            GLOBAL_CONFIG.temp_path,
            retouch_path(split(urlparse(self.host).path)[
                         0]).removeprefix("/").removeprefix("\\")
        ))

        # FFmpeg路徑
        self.ffmpeg_path = "ffmpeg"
        # FFmpeg參數
        self.ffmpeg_args = FFMPEG_ARGS

        self.__logger = getLogger("main")
        self.__block_num = 0       # 區塊數
        self.__block_progress = []  # 區塊進度
        self.__exception = None    # 發生的錯誤

        # 協程列表
        self.tasks: list[Task] = []
        # 是否已經開始下載
        self.started = False
        # 是否已經完成
        self.finish = False
        # 是否被暫停
        self.pause_ = False
        # 是否被停止
        self.stop_ = False

    async def download(self):
        """
        開始下載。
        """
        if self.started:
            return
        client = new_session(headers={
            "referer": "https://v.myself-bbs.com/",
            "origin": "https://v.myself-bbs.com",
        })
        self.started = True
        self.stop_ = False
        self.__logger.info(f"M3U8: 已開始下載`{self.output_name}`。")

        # 取得m3u8檔案內容
        res = await requests(self.m3u8_file, client)
        m3u8_file_content = res.decode()
        # 檢查暫存資料夾是否存在
        if not isdir(self.temp_dir):
            makedirs(self.temp_dir)
        # 解析m3u8檔案
        ts_urls = Queue()
        total_file_list = []
        async with aopen(join(self.temp_dir, "comp_in"), mode="w") as comp_file:
            for line in m3u8_file_content.split("\n"):
                # 範例: 720p_000.ts
                if not line.endswith(".ts"):
                    continue
                # 寫入FFmpeg合成檔
                await comp_file.write(f"file 'f_{line}'\n")
                # 加入貯列
                await ts_urls.put(line)
                total_file_list.append(line)
                # 更新區塊數量
                self.__block_num += 1

        while True:
            # 新增下載協程
            for _ in range(GLOBAL_CONFIG.connections):
                self.tasks.append(create_task(
                    self.__download(ts_urls, client)))
            self.tasks.append(create_task(self.__block_check()))
            # 開始下載
            res = await gather(*self.tasks, return_exceptions=True)

            if "block" in res:
                self.__logger.info(f"M3U8: 檢測到中斷，開始重新下載`{self.output_name}`。")
                self.tasks = []
                for _file in total_file_list:
                    await ts_urls.put(_file)
                continue
            elif False in map(self.__check_file_finish, total_file_list) and self.get_progress() == 1:
                self.__logger.info(
                    f"M3U8: 檢測到文件缺失，開始重新下載`{self.output_name}`。")
                self.tasks = []
                for file in total_file_list:
                    await ts_urls.put(file)
                continue
            break

        await client.close()

        # 如果發生錯誤
        if self.__exception != None:
            self.__logger.error(
                f"M3U8: 已取消下載`{self.output_name}`，錯誤訊息:{''.join(format_exception(self.__exception))}")
            self.started = False
            self.finish = True
            return
        # 如果被取消
        elif self.stop_ == True:
            self.__logger.warning(f"M3U8: 已被取消下載`{self.output_name}`。")
            self.started = False
            self.finish = True
            return
        elif self.stop_ == None:
            self.__logger.info(f"M3U8: 已被中斷下載`{self.output_name}`。")
            self.started = False
            return

        # 檢查輸出資料夾是否存在
        if not isdir(self.output_dir):
            makedirs(self.output_dir)
        # 合成影片
        ffmpeg_commands = [
            self.ffmpeg_path,
            self.ffmpeg_args,
            "-v error -f concat -i",
            "\"" + join(self.temp_dir, "comp_in") + "\"",
            "-c copy -y",
            "\"" + join(self.output_dir, f"{self.output_name}.mp4") + "\"",
        ]

        loop = get_running_loop()
        subprocessres = await loop.run_in_executor(None,
                                                   lambda: run(
                                                       " ".join(
                                                           ffmpeg_commands),
                                                       shell=False, stdout=DEVNULL, stderr=PIPE
                                                   ),
                                                   )
        if subprocessres.stderr != b"":
            if not isdir("ffmpeg-error"):
                makedirs("ffmpeg-error")
            async with aopen(
                f"ffmpeg-error/{datetime.now(tz=TIMEZONE).isoformat().replace(':', '_')}.log",
                mode="wb",
            ) as open_file:
                await open_file.write(subprocessres.stderr)
            self.__logger.error(
                f"M3U8: FFmpeg Error: {subprocessres.stderr.decode()}")
        else:
            self.__clean_up()
        self.__logger.info(f"M3U8: 已完成下載`{self.output_name}`。")
        self.finish = True
        self.started = False

    async def __download(self, url_queue: Queue, client: ClientSession):
        while not url_queue.empty():
            self.__block_progress.append(0)
            block_index = len(self.__block_progress) - 1
            # 取得檔名 (範例: 720p_000.ts)
            file_name = await url_queue.get()

            # 發生錯誤次數
            exception_times = 0
            while True:
                try:
                    # 檢查是否已下載完成
                    if self.__check_file_finish(file_name):
                        # 完成
                        self.__block_progress[block_index] = 1
                        break
                    finish_file_path = join(self.temp_dir, f"f_{file_name}")

                    # 文件路徑
                    file_path = join(self.temp_dir, file_name)

                    # 讀取已下載大小
                    downloaded_size = 0
                    if isfile(file_path):
                        downloaded_size = stat(file_path).st_size
                    # 合成連結
                    url = urljoin(self.host, file_name)

                    # 取得影片
                    stream = await requests(url, client, raw=True, headers={
                        "Range": f"bytes={downloaded_size}-"
                    })
                    # 取得影片大小
                    total_leng = int(stream.headers.get("content-length"))
                    # 開啟檔案
                    async with aopen(file_path, mode="ab") as video:
                        async for chunk in stream.content.iter_chunked(1024):
                            while self.pause_:
                                await sleep(0.1)
                            # 寫入檔案
                            write_leng = await video.write(chunk)
                            # 更新已下載大小
                            downloaded_size += write_leng
                            # 更新下載進度
                            self.__block_progress[block_index] = downloaded_size / total_leng
                    rename(file_path, finish_file_path)
                    # 完成
                    self.__block_progress[block_index] = 1
                    break
                except CancelledError as _cancelled_error:
                    raise _cancelled_error
                except Exception as exception:
                    # 檢查是否超過最大重試次數
                    if exception_times > GLOBAL_CONFIG.retry and GLOBAL_CONFIG.retry != 0:
                        # 停止所有協程
                        self.__logger.error(
                            f"M3U8下載發生錯誤，已達到第 {exception_times} 次重試，將停止下載，連結:`{url}`。")
                        self.__exception = exception
                        for task in self.tasks:
                            if task == current_task():
                                continue
                            task.cancel(f"Exception: {exception}")
                        current_task().cancel(f"Exception: {exception}")
                        raise CancelledError
                    exception_times += 1
                    self.__logger.warning(
                        f"M3U8下載發生錯誤，將於 5 秒後重新下載，第 {exception_times} 次重試，連結:`{url}`。")
                    await sleep(5)
                    continue

    async def __block_check(self):
        alive = True
        while alive:
            start = self.get_progress()
            for _ in range(5):
                await sleep(1)
                prog = self.get_progress()
                alive = prog < 1
                if self.pause_ or not self.started or not alive:
                    break
            if not alive:
                return

            if self.pause_ or not self.started:
                await sleep(1)
                continue

            if prog == start:
                for task in self.tasks:
                    if task == current_task():
                        continue
                    task.cancel(f"")
                return "block"

    def get_progress(self) -> float:
        """
        取得下載進度: 0~1(以區塊數量計算，非真實數值)。

        :return: :class:`float`0~1。
        """
        block_progress = self.__block_progress.copy()
        total_progress = sum(block_progress)

        if self.__block_num == 0:
            return 0

        return min(1, total_progress / self.__block_num)

    def pause(self) -> None:
        if self.started:
            self.pause_ = True

    def resume(self) -> None:
        self.pause_ = False

    def stop(self, clean: bool = False) -> None:
        """
        停止下載。

        :param clean: :class:`bool`停止後是否清除暫存。
        """
        if clean:
            self.stop_ = True
        else:
            self.stop_ = None
        for task in self.tasks:
            task.cancel("")
        if clean:
            self.__clean_up()
            self.finish = True

    def status_code(self) -> int:
        """
        回傳當前狀態碼。
        0: 下載中
        1: 暫停中
        2: 中斷
        3: 完成
        4: 尚未開始
        5: 中止
        6: 發生錯誤

        :param return: :class:`int`0~6。
        """
        if self.started:
            if self.pause_:
                return 1
            return 0
        if self.stop_ == None:
            return 2
        if self.stop_ == False:
            if self.finish:
                return 3
            return 4
        if self.stop_:
            return 5
        return 6

    def status(self) -> str:
        """
        回傳當前狀態。

        :param return: :class:`str`下載中|暫停中|中斷|中止|發生錯誤。
        """
        code = self.status_code()
        return ["下載中", "暫停中", "中斷", "完成", "尚未開始", "中止", "發生錯誤"][code]

    def __check_file_finish(self, file_name: str):
        finish_file_path = join(self.temp_dir, f"f_{file_name}")
        return isfile(finish_file_path)

    def __clean_up(self) -> None:
        if isdir(self.temp_dir):
            rmtree(self.temp_dir)
        recursion_delete_dir("temp")
