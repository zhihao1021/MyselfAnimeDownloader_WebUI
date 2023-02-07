from .cache_manger import Cache

from utils import Json
from configs import BS_FEATURE, GLOBAL_CONFIG

from datetime import timedelta
from logging import getLogger
from traceback import format_exception
from typing import Any, Literal, Optional, Union

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from multidict import CIMultiDictProxy

HEADERS = {
    "user-agent": GLOBAL_CONFIG.user_agent
}
LOGGER = getLogger("main")


def new_session(
    headers: Optional[dict] = None,
    cookies: Optional[dict[str, str]] = None
):
    return ClientSession(
        headers=headers if headers != None else HEADERS.copy(),
        conn_timeout=GLOBAL_CONFIG.timeout,
        cookies=cookies,
    )


async def new_websocket(
    client: Optional[ClientSession] = None
):
    pass


async def requests(
    url: str,
    client: Optional[ClientSession] = None,
    *,
    data: Any = None,
    method: Literal["GET", "POST", "HEAD"] = "GET",
    headers: Optional[dict] = None,
    cookies: Optional[dict[str, str]] = None,
    raw: bool = False,
    soup: bool = False,
    json: bool = False,
    from_cache: bool = False,
    save_cache: bool = False,
    cache_delta: Optional[timedelta] = None,
    timeout: Optional[float] = None,
    allow_redirects: bool = True,
    max_redirects: int = 10,
    raise_exception: bool = False
) -> Optional[Union[bytes, CIMultiDictProxy, ClientResponse, BeautifulSoup]]:
    """
    非同步請求。

    :param url: :class:`str`連結。
    :param client: :class:`ClientSession`對話。
    :param headers: :class:`dict`請求標頭。
    :param cookies: :class:`dict`請求Cookies。
    :param raw: :class:`bool`是否返回原始回應(:class:`ClientResponse`)。
    :param soup: :class:`bool`是否返回BeautifulSoup。
    :param json: :class:`bool`是否返回Json解碼後的資料。
    :param from_cache: :class:`bool`是否從快取讀取。
    :param save_cache: :class:`bool`是否將資料儲存至快取。
    :param cache_delta: :class:`bool`快取有效時間。
    :param timeout: :class:`float`Timeout。
    :param allow_redirects: :class:`bool`使否允許重新導向。
    :param max_redirects: :class:`int`最大重新導向次數。
    :param raise_exception: :class:`bool`發生錯誤時是否回傳。

    :return: :class:`Optional[Union[bytes, CIMultiDictProxy, ClientResponse, BeautifulSoup]]`
    """
    try:
        method = method.upper()
        save_cache = True if from_cache else save_cache
        # 檢查是否從快取讀取
        if not from_cache or raw or method == "HEAD":
            pass
        # 檢查快取是否有限時間
        elif cache_delta == None:
            # 檢查資源是否已快取
            if Cache.is_cached(url):
                if soup:
                    return BeautifulSoup(
                        await Cache.read_cache(url),
                        features=BS_FEATURE
                    )
                elif json:
                    return Json.loads(await Cache.read_cache(url))
                return await Cache.read_cache(url)
        # 檢查快取是否超時
        elif Cache.get_update_delta(url) < cache_delta:
            if soup:
                return BeautifulSoup(
                    await Cache.read_cache(url),
                    features=BS_FEATURE
                )
            elif json:
                return Json.loads(await Cache.read_cache(url))
            return await Cache.read_cache(url)

        # 檢查是否需要開新連線
        need_close = False if client else True
        client = client if client else new_session(
            headers=headers, cookies=cookies)

        kwargs = {
            "url": url,
            "allow_redirects": allow_redirects,
            "max_redirects": max_redirects,
            "ssl": False
        }
        # 判斷請求方式
        if method == "HEAD":
            __request = client.head
        elif method == "POST":
            __request = client.post
            if type(data) in [dict, list]:
                data = Json.dumps(data)
            kwargs["data"] = data
        else:
            __request = client.get

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
        cache = None
        if raw:
            result = res
        elif method == "HEAD":
            result = res.headers.copy()
        elif soup:
            cache = await res.content.read()
            result = BeautifulSoup(
                cache,
                features=BS_FEATURE
            )
        elif json:
            result = await res.json()
        else:
            cache = await res.content.read()
            result = cache

        if save_cache and cache:
            # 寫入快取
            await Cache.write_cache(url, cache)

        # 檢查是否需要關閉連線
        if need_close:
            await client.close()

        # 回傳
        return result
    except Exception as exc:
        exc_text = "".join(format_exception(exc))
        LOGGER.error(f"Requests Error: {exc_text}")
        # 檢查是否需要關閉連線
        try:
            if need_close:
                await client.close()
        except UnboundLocalError:
            pass
        # 檢查是否需要回傳錯誤
        if raise_exception:
            raise exc
        return None
