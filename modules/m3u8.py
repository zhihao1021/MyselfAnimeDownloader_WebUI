from async_io import new_session, requests

from aiohttp import ClientSession
from asyncio import create_task, gather, Queue
from os.path import abspath, join, isfile
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
        self.host = host
        if not self.host.endswith("/"):
            self.host += "/"
        self.m3u8_file = m3u8_file
        self.output_name = output_name

        if output_dir == None: self.output_dir = "download"
        else: self.output_dir = abspath(output_dir)

        if temp_dir == None: self.temp_dir = "temp"
        else: self.temp_dir = temp_dir
        _paths = urlparse(self.host).path.split("/")
        self.temp_dir = abspath(join(self.temp_dir, *_paths))

        if ffmpeg_path == None: self.ffmpeg_path = "ffmpeg"
        else:
            if isfile(ffmpeg_path):
                self.ffmpeg_path = abspath(ffmpeg_path)
            else:
                self.ffmpeg_path = abspath(join(ffmpeg_path, "ffmpeg"))

        if ffmpeg_args == None: self.ffmpeg_args = ()
        else: self.ffmpeg_args = ffmpeg_args
    
    async def download(self, connections: int=3, _client: Optional[ClientSession]=None):
        """
        開始下載。

        connections: :class:`int`
            連接數量。
        """
        need_close = False
        if _client == None:
            _client = new_session()
            need_close = True

        _res = await requests(self.m3u8_file, _client)
        m3u8_file_content = _res.decode()
        _ts_urls = Queue()
        with open(join(self.temp_dir, "comp_in"), mode="w") as _comp_file:
            for _line in m3u8_file_content.split("\n"):
                if not _line.endswith(".ts"): continue
                _comp_file.write(f"file '{_line}'\n")
                _ts_urls.put_nowait(_line)
        
        tasks = []
        for _ in range(connections):
            tasks.append(create_task(self._download(_ts_urls, _client)))
        await gather(*tasks)

        if need_close: await _client.close()
    
    async def _download(self, url_queue: Queue, _client: Optional[ClientSession]=None):
        need_close = False
        if _client == None:
            _client = new_session()
            need_close = True

        while not url_queue.empty():
            _file_name = await url_queue.get()
            _process_file = join(self.temp_dir, f"{_file_name}.p")
            if isfile(_process_file):
                pass
            else:
                requests()
            _url = urljoin(self.host, _file_name)

        if need_close: await _client.close()
        