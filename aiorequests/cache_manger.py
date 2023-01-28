from configs import TIMEZONE

from datetime import datetime, timedelta
from os import makedirs
from os.path import getmtime, isfile, isdir, join, split as ossplit
from typing import Union
from urllib.parse import urlsplit
from utils import retouch_name

from aiofiles import open as aopen


def url2cache_path(url: str) -> tuple[str, str]:
    """
    :return: dirpath, filepath
    """
    res = urlsplit(url)
    loc = retouch_name(res.netloc)
    query = tuple(map(retouch_name, res.query.split("&")))
    path = tuple(map(retouch_name, res.path.split("/")))

    result = join("cache", loc, *query, *path)

    return ossplit(result)[0], result


class Cache:
    @staticmethod
    def is_cached(url: str) -> bool:
        """
        檢查快取中是否存在該資源。
        """
        _, cache_path = url2cache_path(url)
        return isfile(cache_path)

    @staticmethod
    async def read_cache(url: str) -> bytes:
        """
        從快取中讀取資源。
        """
        _, cache_path = url2cache_path(url)
        async with aopen(cache_path, mode="rb") as open_file:
            return await open_file.read()

    @staticmethod
    def read_cache_nowait(url: str) -> bytes:
        """
        從快取中讀取資源(blocking)。
        """
        _, cache_path = url2cache_path(url)
        with open(cache_path, mode="rb") as open_file:
            return open_file.read()

    @staticmethod
    async def write_cache(url: str, content: Union[bytes, str]) -> int:
        """
        將資源寫入快取。
        """
        cache_dir, cache_path = url2cache_path(url)
        if not isdir(cache_dir):
            makedirs(cache_dir)

        # 寫入資料
        async with aopen(cache_path, mode="wb") as open_file:
            return await open_file.write(content)

    @staticmethod
    def write_cache_nowait(url: str, content: Union[bytes, str]) -> int:
        """
        將資源寫入快取(blocking)。
        """
        cache_dir, cache_path = url2cache_path(url)
        if not isdir(cache_dir):
            makedirs(cache_dir)

        # 寫入資料
        with open(cache_path, mode="wb") as open_file:
            return open_file.write(content)

    @staticmethod
    def get_update_time(url: str) -> datetime:
        _, cache_path = url2cache_path(url)
        if isfile(cache_path):
            return datetime.fromtimestamp(getmtime(cache_path), tz=TIMEZONE)
        return datetime.fromtimestamp(0, tz=TIMEZONE)

    @staticmethod
    def get_update_delta(url: str) -> timedelta:
        return datetime.now(tz=TIMEZONE) - Cache.get_update_time(url)
