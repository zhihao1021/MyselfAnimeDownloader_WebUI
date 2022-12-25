from modules import Json
from configs import UA, TIMEOUT, MAIN_LOGGER

from traceback import format_exception
from typing import Any, Literal, Optional, Union

from aiohttp import ClientSession, ClientResponse

HEADERS = {
    "User-Agent": UA
}

def new_session(cookies: Optional[dict[str, str]]=None):
    return ClientSession(
        headers=HEADERS,
        read_timeout=TIMEOUT,
        cookies=cookies
    )

async def requests(
    url: str,
    _client: Optional[ClientSession]=None,
    *,
    data: Any=None,
    method: Literal["GET", "POST", "HEAD"]="GET",
    cookies: Optional[dict[str, str]]=None,
    raw: bool=False
) -> Optional[Union[str, dict, ClientResponse]]:
    """
    非同步請求。

    url: :class:`str`
        連結。
    method: :class:`Literal["GET", "POST", "HEAD"]`
        請求方法。
    
    return: :class:`Optional[Union[bytes, dict]]`
    """
    try:
        method = method.upper()
        need_close = False

        if type(data) in [dict, list]: data = Json.dumps(data)
        if _client == None:
            _client = new_session(cookies)
            need_close = True

        if method == "HEAD": _res = await _client.head(url)
        elif method == "POST": _res = await _client.post(url, data=data)
        else: _res = await _client.get(url)

        if need_close: await _client.close()
        
        if raw: return _res
        if method == "HEAD":
            return dict(_res.headers)
        return await _res.content.read()
    except Exception as _exc:
        _exc_text = "".join(format_exception(_exc))
        MAIN_LOGGER.error(_exc_text)
    return None
