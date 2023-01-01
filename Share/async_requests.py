from logging import getLogger
from traceback import format_exception
from typing import Any, Literal, Optional, Union

from aiohttp import ClientSession, ClientResponse
from multidict import CIMultiDictProxy
from orjson import dumps

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0 (Edition GX-CN)"
}
TIMEOUT = 5

MAIN_LOGGER = getLogger("main")

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
) -> Optional[Union[bytes, CIMultiDictProxy, ClientResponse]]:
    """
    非同步請求。

    url: :class:`str`
        連結。
    method: :class:`Literal["GET", "POST", "HEAD"]`
        請求方法。
    
    return: :class:`Optional[Union[bytes, CIMultiDictProxy, ClientResponse]]`
    """
    try:
        method = method.upper()
        need_close = False

        if type(data) in [dict, list]: data = dumps(data)
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
        
        if raw: result = _res
        elif method == "HEAD":
            result = _res.headers.copy()
        else: result = await _res.content.read()

        if need_close: await _client.close()
        
        return result
    except Exception as _exc:
        _exc_text = "".join(format_exception(_exc))
        MAIN_LOGGER.error(_exc_text)
    return None
