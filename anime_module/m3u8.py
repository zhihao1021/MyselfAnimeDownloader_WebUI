from async_io import new_session, requests
from configs import *

from asyncio import CancelledError, create_task, current_task, gather, Lock, Queue, sleep, Task
from datetime import datetime
from os import makedirs, rename, rmdir, stat, walk
from os.path import abspath, join, isfile, isdir
from shutil import rmtree
from subprocess import run, DEVNULL, PIPE
from traceback import format_exception
from typing import Optional
from urllib.parse import urljoin, urlparse

from aiofiles import open as a_open
from aiohttp import ClientSession

def _ce_dir(dir_path: str):
    _d = 0
    for _path, _folder, _file in walk(dir_path, topdown=False):
        if _folder == [] and _file == []:
            try:
                rmdir(_path)
                _d += 1
            except: pass
    if _d: _ce_dir(dir_path)

class M3U8:
    def __init__(self,
        host: str,
        m3u8_file: str,
        output_name: str,
        output_dir: Optional[str]=None,
    ) -> None:
        """
        M3U8下載器。

        host: :class:`str`
            主機位置。
        m3u8file: :class:`str`
            .m3u8文件位置。
        output_name: :class:`str`
            輸出檔案名稱。
        output_dir: :class:`str`
            輸出資料夾位置。
        """
        # 主機位置
        self.host = host
        if not self.host.endswith("/"):
            self.host += "/"
        # 檔案位置
        self.m3u8_file = m3u8_file
        # 輸出檔名
        self.output_name = output_name

        # 輸出資料夾
        if output_dir == None: self.output_dir = "download"
        else: self.output_dir = abspath(output_dir)

        # 暫存資料夾
        self.temp_dir = TEMP_PATH
        _paths = urlparse(self.host).path.split("/")
        self.temp_dir = abspath(join(self.temp_dir, *_paths))

        # FFmpeg路徑
        self.ffmpeg_path = "ffmpeg"

        # FFmpeg參數
        self.ffmpeg_args = FFMPEG_ARGS

        self._block_num = 0       # 區塊數
        self._block_progress = [] # 區塊進度
        self._exception = None    # 發生的錯誤
        self._lock = Lock()       # 協程鎖，暫停下載用

        # 協程列表
        self.tasks: list[Task] = []
        # 是否已經開始下載
        self.started = False
        # 是否被暫停
        self._pause = False
        # 是否被停止
        self._stop = False
    
    async def download(self):
        """
        開始下載。
        """
        if self.started: return
        _client = new_session(headers={
            "referer": "https://v.myself-bbs.com/",
            "origin": "https://v.myself-bbs.com",
        })

        # 取得m3u8檔案內容
        _res = await requests(self.m3u8_file, _client)
        m3u8_file_content = _res.decode()
        # 檢查暫存資料夾是否存在
        if not isdir(self.temp_dir):
            makedirs(self.temp_dir)
        # 解析m3u8檔案
        _ts_urls = Queue()
        with open(join(self.temp_dir, "comp_in"), mode="w") as _comp_file:
            for _line in m3u8_file_content.split("\n"):
                if not _line.endswith(".ts"): continue
                # 範例: 720p_000.ts
                # 寫入FFmpeg合成檔
                _comp_file.write(f"file 'f_{_line}'\n")
                # 加入貯列
                _ts_urls.put_nowait(_line)
                # 更新區塊數量
                self._block_num += 1
        
        # 新增下載協程
        for _ in range(CONS):
            self.tasks.append(create_task(self._download(_ts_urls, _client)))
        self.tasks.append(create_task(self._lock_task()))
        # 開始下載
        self.started = True
        res = await gather(*self.tasks, return_exceptions=True)
        print(res)

        await _client.close()

        # 如果發生錯誤
        if self._exception != None:
            MAIN_LOGGER.error(f"M3U8已取消下載`{self.output_name}`，錯誤訊息:{' '.join(format_exception(self._exception))}")
            self.started = False
            return
        # 如果被取消
        elif self._stop:
            MAIN_LOGGER.warning(f"M3U8已被取消下載`{self.output_name}`。")
            self.started = False
            return


        # 檢查輸出資料夾是否存在
        if not isdir(self.output_dir):
            makedirs(self.output_dir)
        # 合成影片
        _ffmpeg_commands = [
            self.ffmpeg_path,
            self.ffmpeg_args,
            "-v error -f concat -i",
            "\"" + join(self.temp_dir, "comp_in") + "\"",
            "-c copy -y",
            "\"" + join(self.output_dir, f"{self.output_name}.mp4") + "\"",
        ]
        _subprocess_res = run(
            " ".join(_ffmpeg_commands),
            shell=False, stdout=DEVNULL, stderr=PIPE
        )
        if _subprocess_res.stderr != b"":
            open(f"{datetime.now(TIMEZONE).isoformat().replace(':', '_')}_ffmpeg_error.log", mode="wb").write(
                _subprocess_res.stderr
            )
        else:
            self._clean_up()
        self.started = False
    
    async def _download(self, url_queue: Queue, _client: ClientSession):
        while not url_queue.empty():
            self._block_progress.append(0)
            _block_index = len(self._block_progress) - 1
            # 取得檔名 (範例: 720p_000.ts)
            _file_name = await url_queue.get()

            # 發生錯誤次數
            _exception_times = 0
            while True:
                try:
                    # 檢查是否已下載完成
                    _finish_file_path = join(self.temp_dir, f"f_{_file_name}")
                    if isfile(_finish_file_path):
                        # 完成
                        self._block_progress[_block_index] = 1
                        continue

                    # 文件路徑
                    _file_path = join(self.temp_dir, _file_name)

                    # 讀取已下載大小
                    _downloaded_size = 0
                    if isfile(_file_path):
                        _downloaded_size = stat(_file_path).st_size
                    
                    # 合成連結
                    _url = urljoin(self.host, _file_name)

                    # 取得影片
                    _stream = await requests(_url, _client, raw=True, headers={
                        "Range": f"bytes={_downloaded_size}-"
                    })
                    # 取得影片大小
                    _total_leng = int(_stream.headers.get("content-length"))
                    # 開啟檔案
                    async with a_open(_file_path, mode="ab") as _video:
                        async for chunk in _stream.content.iter_chunked(1024):
                            await self._lock.acquire()
                            # 寫入檔案
                            _write_leng = await _video.write(chunk)
                            # 更新已下載大小
                            _downloaded_size += _write_leng
                            # 更新下載進度
                            self._block_progress[_block_index] = _downloaded_size / _total_leng
                            self._lock.release()
                    break
                except CancelledError as _cancelled_error:
                    raise _cancelled_error
                except Exception as _exception:
                    # 檢查是否超過最大重試次數
                    if _exception_times > RETRY:
                        # 停止所有協程
                        MAIN_LOGGER.error(f"M3U8下載發生錯誤，已達到第 {_exception_times} 次重試，將停止下載，連結:`{_url}`。")
                        self._exception = _exception
                        for task in self.tasks:
                            if task == current_task(): continue
                            task.cancel(f"Exception: {_exception}")
                        current_task().cancel(f"Exception: {_exception}")
                        raise CancelledError
                    _exception_times += 1
                    MAIN_LOGGER.warning(f"M3U8下載發生錯誤，將於 5 秒後重新下載，第 {_exception_times} 次重試，連結:`{_url}`。")
                    await sleep(5)
                    continue
            rename(_file_path, _finish_file_path)
            # 完成
            self._block_progress[_block_index] = 1
    
    async def _lock_task(self):
        _alive = True
        while _alive:
            if self._pause:
                await self._lock.acquire()
                while self._pause: await sleep(0.1)
                self._lock.release()
            await sleep(0.2)
            _alive = list(map(lambda x: x.done(), self.tasks)).count(False) > 1
            
    def get_progress(self) -> float:
        """
        取得下載進度: 0~1(以區塊數量計算，非真實數值)。
        """
        _total_progress = sum(self._block_progress)

        if self._block_num == 0:
            return 0

        return min(1, _total_progress / self._block_num)
    
    def pause(self) -> None:
        self._pause = True
    
    def resume(self) -> None:
        self._pause = False
    
    def stop(self, clean: bool=False) -> None:
        """
        停止下載。

        clean: :class:`bool`
            停止後是否清除暫存。
        """
        for task in self.tasks:
            task.cancel("")
        if clean:
            self._clean_up()
    
    def _clean_up(self) -> None:
        rmtree(self.temp_dir)
        _ce_dir(self.temp_dir)