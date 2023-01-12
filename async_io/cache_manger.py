from configs import *

from asyncio import Lock
from datetime import datetime
from os import makedirs
from os.path import isfile, isdir, join, split as ossplit
from urllib.parse import urlsplit

from aiofiles import open as a_open
from aiosqlite import connect

_STRIP = " \"\n\r"
BAN_CHAR = "\\/:*?\"<>|"

def _retouch_name(name: str) -> str:
    """
    避免不正當名字出現導致資料夾或檔案無法創建。
    name: :class:`str`
        輸入字串。

    return: :class:`str`
        修飾後字串。
    """
    for char in BAN_CHAR: name = name.replace(char, " ")
    return name.strip(_STRIP)

def _url2cache_path(url: str) -> str:
    _res = urlsplit(url)
    _loc = _retouch_name(_res.netloc)
    _query = list(map(_retouch_name, _res.query.split("&")))
    _path = list(map(_retouch_name, _res.path.split("/")))

    _result = join("cache", _loc, *_query, *_path)

    return ossplit(_result)[0], _result

class Cache:
    @staticmethod
    def is_cached(url: str) -> bool:
        _, _cache_path = _url2cache_path(url)
        return isfile(_cache_path)
    
    @staticmethod
    async def read_cache(url: str) -> bytes:
        _, _cache_path = _url2cache_path(url)
        if not isfile(_cache_path):
            raise FileNotFoundError
        async with a_open(_cache_path, mode="rb") as _file:
            return await _file.read()
    
    @staticmethod
    async def write_cache(url: str, content: bytes) -> int:
        _cache_dir, _cache_path = _url2cache_path(url)
        if not isdir(_cache_dir):
            makedirs(_cache_dir)
        
        async with connect("data.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "SELECT update_time FROM cache WHERE url=:url",
                    {"url": url}
                )
                if await cursor.fetchone() != None:
                    await cursor.execute(
                        "UPDATE cache SET update_time=:update_time WHERE url=:url",
                        {"update_time": datetime.now(TIMEZONE).isoformat(), "url": url}
                    )
                else:
                    await cursor.execute(
                        "INSERT INTO cache (url, update_time) VALUES (:url, :update_time)",
                        {"update_time": datetime.now(TIMEZONE).isoformat(), "url": url}
                    )
            await db.commit()

        async with a_open(_cache_path, mode="wb") as _file:
            return await _file.write(content)
    
    @staticmethod
    async def get_update_time(url: str) -> datetime:
        async with connect("data.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "SELECT update_time FROM cache WHERE url=:url",
                    {"url": url}
                )
                _res = await cursor.fetchone()
                if _res == None:
                    return datetime.fromtimestamp(0, TIMEZONE)
                _res = _res[0]
                
                _, _cache_path = _url2cache_path(url)
                if not isfile(_cache_path):
                    await cursor.execute(
                        "DELETE FROM cache WHERE url=:url",
                        {"url": url}
                    )
                    await db.commit()
                    return datetime.fromtimestamp(0, TIMEZONE)
                return datetime.fromisoformat(_res)
