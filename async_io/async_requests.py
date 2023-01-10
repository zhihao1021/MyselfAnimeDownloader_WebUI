from .cache_manger import Cache

from modules import Json
from configs import UA, TIMEOUT, MAIN_LOGGER

from os import makedirs
from os.path import isfile, isdir, join, split as ossplit
from traceback import format_exception
from typing import Any, Literal, Optional, Union

from aiohttp import ClientSession, ClientResponse
from multidict import CIMultiDictProxy

HEADERS = {
    "user-agent": UA
}

def new_session(headers: Optional[dict]=None, cookies: Optional[dict[str, str]]=None):
    _headers = HEADERS.copy()
    if headers != None:
        _headers.update(headers)
    return ClientSession(
        headers=_headers,
        conn_timeout=TIMEOUT,
        cookies=cookies,
    )

async def requests(
    url: str,
    _client: Optional[ClientSession]=None,
    *,
    data: Any=None,
    method: Literal["GET", "POST", "HEAD"]="GET",
    headers: Optional[dict]=None,
    cookies: Optional[dict[str, str]]=None,
    raw: bool=False,
    from_cache: bool=False
) -> Optional[Union[bytes, CIMultiDictProxy, ClientResponse]]:
    """
    非同步請求。

    url: :class:`str`
        連結。
    method: :class:`Literal["GET", "POST", "HEAD"]`
        請求方法。
    from_cache: :class:`bool`
        是否從硬碟快取讀取。
    
    return: :class:`Optional[Union[bytes, CIMultiDictProxy, ClientResponse]]`
    """
    try:
        method = method.upper()
        need_close = False

        if from_cache:
            if Cache.is_cached(url):
                return await Cache.read_cache(url)

        if type(data) in [dict, list]: data = Json.dumps(data)
        if _client == None:
            _client = new_session(cookies)
            need_close = True
        
        if headers != None:
            _headers = _client.headers.copy()
            _headers.update(headers)
            if method == "HEAD": _res = await _client.head(url, headers=_headers)
            elif method == "POST": _res = await _client.post(url, data=data, headers=_headers)
            else: _res = await _client.get(url, headers=_headers)
        else:
            if method == "HEAD": _res = await _client.head(url)
            elif method == "POST": _res = await _client.post(url, data=data)
            else: _res = await _client.get(url)
        
        if raw:
            result = _res
        elif method == "HEAD":
            result = _res.headers.copy()
        else:
            result = await _res.content.read()

            if from_cache or Cache.is_cached(url):
                await Cache.write_cache(url, result)

        if need_close: await _client.close()
        
        return result
    except Exception as _exc:
        _exc_text = "".join(format_exception(_exc))
        MAIN_LOGGER.error(f"Requests Error: {_exc_text}")
    return None
