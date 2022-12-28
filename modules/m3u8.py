from async_io import new_session, requests

from aiohttp import ClientSession
from aiofiles import open as a_open
from asyncio import create_task, gather, Queue
from os import stat, rename
from os.path import abspath, join, isfile
from subprocess import run, DEVNULL, PIPE
from typing import Optional
from urllib.parse import urljoin, urlparse

class M3U8:
    def __init__(self,
        host: str,
        m3u8_file: str,
        output_name: str,
        output_dir: Optional[str]=None,
        temp_dir: Optional[str]=None,
        ffmpeg_path: Optional[str]=None,
        ffmpeg_args: Optional[tuple]=None,
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
        temp_dir: :class:`str`
            暫存資料夾位置。
        ffmpeg_path: :class:`str`
            ffmpeg位置。
        ffmpeg_args: :class:`tuple`
            ffmpeg參數。
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
        if temp_dir == None: self.temp_dir = "temp"
        else: self.temp_dir = temp_dir
        _paths = urlparse(self.host).path.split("/")
        self.temp_dir = abspath(join(self.temp_dir, *_paths))

        # FFmpeg路徑
        if ffmpeg_path == None: self.ffmpeg_path = "ffmpeg"
        else:
            if isfile(ffmpeg_path):
                self.ffmpeg_path = abspath(ffmpeg_path)
            else:
                self.ffmpeg_path = abspath(join(ffmpeg_path, "ffmpeg"))

        # FFmpeg參數
        if ffmpeg_args == None: self.ffmpeg_args = ()
        else: self.ffmpeg_args = ffmpeg_args

        self._block_num = 0
        self._block_progress = []
    
    async def download(self, connections: int=3):
        """
        開始下載。

        connections: :class:`int`
            連接數量。
        """
        _client = new_session(headers={
            "referer": "https://v.myself-bbs.com/"
        })

        # 取得m3u8檔案內容
        _res = await requests(self.m3u8_file, _client)
        m3u8_file_content = _res.decode()
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
        tasks = []
        for _ in range(connections):
            tasks.append(create_task(self._download(_ts_urls, _client)))
        # 開始下載
        await gather(*tasks)

        await _client.close()

        # 合成影片
        _ffmpeg_commands = [
            self.ffmpeg_path,
            " ".join(self.ffmpeg_args),
            "-v error -f concat -i"
            "\"" + join(self.temp_dir, "comp_in") + "\"",
            "-c copy -y",
            "\"" + join(self.output_dir, f"{self.output_name}.mp4") + "\"",
        ]
        _subprocess_res = run(
            " ".join(_ffmpeg_commands),
            shell=False, stdout=DEVNULL, stderr=PIPE
        )
        if _subprocess_res.stderr.
    
    async def _download(self, url_queue: Queue, _client: ClientSession):
        while not url_queue.empty():
            self._block_progress.append(0)
            _block_index = len(self._block_progress) - 1
            # 取得檔名 (範例: 720p_000.ts)
            _file_name = await url_queue.get()

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
                    # 寫入檔案
                    _write_leng = await _video.write(chunk)
                    # 更新已下載大小
                    _downloaded_size += _write_leng
                    # 更新下載進度
                    self._block_progress[_block_index] = _downloaded_size / _total_leng
            # 完成
            self._block_progress[_block_index] = 1

    def get_progress(self) -> float:
        """
        取得下載進度: 0~1(以區塊數量計算，非真實數值)。
        """
        _total_progress = sum(self._block_progress)

        return _total_progress / self._block_progress