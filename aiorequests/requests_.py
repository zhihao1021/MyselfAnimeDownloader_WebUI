from .cache_manger import Cache

from utils import Json
from configs import GLOBAL_CONFIG

from logging import getLogger
from traceback import format_exception
from typing import Any, Literal, Optional, Union

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from multidict import CIMultiDictProxy

HEADERS = {
    "user-agent": GLOBAL_CONFIG.user_agent
}
LOGGER = getLogger("main")

def new_session(
    headers: Optional[dict]=None,
    cookies: Optional[dict[str, str]]=None
):
    return ClientSession(
        headers=headers if headers != None else HEADERS.copy(),
        conn_timeout=GLOBAL_CONFIG.timeout,
        cookies=cookies,
    )

async def requests(
    url: str,
    client: Optional[ClientSession]=None,
    *,
    data: Any=None,
    method: Literal["GET", "POST", "HEAD"]="GET",
    headers: Optional[dict]=None,
    cookies: Optional[dict[str, str]]=None,
    raw: bool=False,
    from_cache: bool=False,
    save_cache: bool=False,
    timeout: Optional[float]=None,
    allow_redirects: bool = True,
    max_redirects: int = 10
) -> Optional[Union[bytes, CIMultiDictProxy, ClientResponse]]:
    """
    非同步請求。

    url: :class:`str`
        連結。
    method: :class:`Literal["GET", "POST", "HEAD"]`
        請求方法。
    from_cache: :class:`bool`
        是否從硬碟快取讀取。
    save_cache: :class:`bool`
        是否將快取儲存至硬碟。
    
    return: :class:`Optional[Union[bytes, CIMultiDictProxy, ClientResponse]]`
    """
    try:
        # 檢查是否從快取讀取
        if from_cache:
            save_cache = True
            if Cache.is_cached(url):
                return await Cache.read_cache(url)
        
        # 檢查是否需要開新連線
        need_close = False
        if client == None:
            client = new_session(headers=headers, cookies=cookies)
            need_close = True
        
        kwargs = {
            "url": url,
            "allow_redirects": allow_redirects,
            "max_redirects": max_redirects
        }
        # 判斷請求方式
        method = method.upper()
        if method == "HEAD":
            __request = client.head
        elif method == "POST":
            __request = client.post
            if type(data) in [dict, list]:
                data = Json.dumps(data)
            kwargs["data"] = data
        else:
            __request = client.get()
        
        # 檢查是否需要新增標頭
        if headers != None:
            kwargs["headers"] = headers
        # 檢查是否需要新增Cookies
        if cookies != None:
            kwargs["cookies"] = cookies
        # 檢查Timeout
        if timeout != None:
            kwargs["timeout"] = ClientTimeout(connect=timeout)
        
        # 發送請求
        res = await __request(**kwargs)
        
        # 設置回傳值
        if raw:
            result = res
        elif method == "HEAD":
            result = res.headers.copy()
        else:
            result = await res.content.read()
            if save_cache:
                # 寫入快取
                await Cache.write_cache(url, result)

        # 檢查是否需要關閉連線
        if need_close:
            await client.close()
        
        # 回傳
        return result
    except Exception as exc:
        exc_text = "".join(format_exception(exc))
        LOGGER.error(f"Requests Error: {exc_text}")
        # 檢查是否需要關閉連線
        if need_close:
            await client.close()
        return None
