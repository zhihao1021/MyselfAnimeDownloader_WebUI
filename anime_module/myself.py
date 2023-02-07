from .m3u8 import M3U8

from aiorequests import new_session, Cache, requests
from configs import MYSELF_CONFIG, MYSELF_URL
from utils import Json, retouch_name

from asyncio import create_task, gather, sleep as asleep, Task
from datetime import timedelta
from logging import getLogger
from os.path import join, split as split
from traceback import format_exception
from typing import Any, Optional, Union
from unicodedata import normalize
from urllib.parse import parse_qs, urlencode, urljoin

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from html import unescape
from pydantic import BaseModel, Field, validator
from websockets.client import connect as ws_connect, WebSocketClientProtocol

STRIP = " \"\n\r"
UNICODE_CODE = "NFKC"
MYSELF_LOGGER = getLogger("myself")


class ValidAssignmentModel(BaseModel):
    class Config:
        validate_assignment = True


class MyselfAnime(ValidAssignmentModel):
    """
    Myself影片。

    :param episode-name: :class:`str`集數名稱。
    :param tid: :class:`str`動畫ID。
    :param vid: :class:`str`影片ID。
    """
    ANI_NAME: str = Field(alias="animate-name")  # 名稱
    EPS_NAME: str = Field(alias="episode-name")  # 集數名稱
    TID: str = Field(alias="tid")                   # 動畫ID
    VID: str = Field(alias="vid")                   # 影片ID

    @validator("ANI_NAME", "EPS_NAME")
    def eps_name_validator(cls, value: str):
        return normalize(UNICODE_CODE, retouch_name(value))

    @validator("*")
    def all_validator(cls, value: str):
        return value.strip(STRIP)

    async def get_m3u8_url(
        self,
        client: Optional[ClientSession] = None
    ) -> tuple[str, str]:
        """
        取得m3u8連結。

        :param client: :class:`ClientSession`對話。

        :return: :class:`tuple[str, str]`(m3u8主機位置, m3u8檔案位置)。
        """
        # 檢查是否需要開新連線
        need_close = False if client else True
        client = client if client else new_session()

        __ws = await client.ws_connect(
            url="wss://v.myself-bbs.com/ws",
            origin="https://v.myself-bbs.com",
            ssl=False
        )

        await __ws.send_json(
            {"tid": self.TID, "vid": self.VID, "id": ""}
            if self.VID.isdigit() else {"tid": "", "vid": "", "id": self.VID},
            dumps=Json.dumps
        )

        data = await __ws.receive_json(loads=Json.loads)

        m3u8_file = urljoin("https://", data["video"])
        m3u8_server = split(m3u8_file)[0]

        # 檢查是否需要關閉連線
        if need_close:
            await client.close()

        # 回傳
        return m3u8_server, m3u8_file

    async def gen_downloader(self) -> M3U8:
        """
        取得M3U8下載器。
        """
        def translate(string): return string.replace(
            "$NAME", self.ANI_NAME).replace("$EPS", self.EPS_NAME)
        m3u8_host, m3u8_file = await self.get_m3u8_url()
        output_name = translate(MYSELF_CONFIG.file_name)
        output_dir = MYSELF_CONFIG.download_path
        if MYSELF_CONFIG.classify:
            output_dir = join(output_dir, translate(MYSELF_CONFIG.dir_name))
        return M3U8(
            host=m3u8_host,
            m3u8_file=m3u8_file,
            output_name=output_name,
            output_dir=output_dir
        )


class MyselfAnimeTable(ValidAssignmentModel):
    """
    Myself動畫資料。

    :param url: :class:`str`網址。
    :param name: :class:`str`在不更新的情形下指定名稱(用於列表)。
    :param image-url: :class:`str`在不更新的情形下指定縮圖(用於完結列表)。
    """
    URL: str = Field(alias="url")
    TID: Optional[str] = Field(alias="tid")
    NAME: Optional[str] = Field(alias="name")
    ANI_TYPE: Optional[str] = Field(alias="animate-type")
    PRE_DATE: Optional[str] = Field(alias="premiere-date")
    EPS_NUM: Optional[str] = Field(alias="episode-num")
    AUTHOR: Optional[str] = Field(alias="author")
    OFFICIAL_WEB: Optional[str] = Field(alias="offical-website")
    REMARKS: Optional[str] = Field(alias="remarks")
    INTRO: Optional[str] = Field(alias="introduction")
    IMAGE_URL: Optional[str] = Field(alias="image-url")
    VIDEO_LIST: list[MyselfAnime] = Field([], alias="video-list")
    updated: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TID = self.URL.split("/")[-1].split("-")[1]

    @validator("NAME")
    def name_validator(cls, value: str):
        return normalize(UNICODE_CODE, retouch_name(value))

    @validator("*")
    def all_validator(cls, value: Union[str, Any]):
        if type(value) == str:
            value = value.strip(STRIP)
        return value

    async def update(
        self,
        client: Optional[ClientSession] = None,
        from_cache=True
    ) -> None:
        """
        更新資料。

        :param client: :class:`ClientSession`對話。
        :param from_cache: :class:`bool`是否從硬碟快取讀取。
        """
        soup = await requests(
            url=self.URL,
            client=client,
            soup=True,
            from_cache=from_cache,
            save_cache=True,
        )

        # 檢查是否來自快取
        if not from_cache:
            pass
        # 檢查是否為完結動畫
        elif soup.select_one("div.z a[href='forum-113-1.html']"):
            pass
        # 檢查距離上次更新是否超過12小時
        elif Cache.get_update_delta(self.URL) > timedelta(hours=12):
            # 重新抓取資料
            soup = await requests(
                url=self.URL,
                client=client,
                soup=True,
                from_cache=False,
                save_cache=True,
            )

        self.NAME = soup.select_one("meta[name='keywords']")["content"]
        self.INTRO = soup.select_one("#info_introduction_text").text
        self.IMAGE_URL = soup.select_one("div.info_img_box img")["src"]

        # 資訊欄列表
        info_list = map(
            lambda tag: tag.text.split(":", 1)[1],
            soup.select("div.info_info li")
        )
        for info, attr_name in zip(info_list, ["ANI_TYPE", "PRE_DATE", "EPS_NUM", "AUTHOR", "OFFICIAL_WEB", "REMARKS"]):
            self.__setattr__(attr_name, info)

        # 動畫列表
        self.VIDEO_LIST = [
            MyselfAnime(**{
                "animate-name": self.NAME,
                "episode-name": episode_name,
                "tid": self.TID,
                "vid": split(a_tag["data-href"])[1]
            })
            for a_tag, episode_name in map(
                lambda tag: (tag.select_one(
                    "a[data-href*=myself]"), tag.select_one("a").text),
                soup.select("ul.main_list > li")
            )
        ]

        self.updated = True


class Myself:
    @staticmethod
    async def weekly_update(
        update: bool = False,
        client: Optional[ClientSession] = None,
        from_cache=True
    ) -> list[list[tuple[MyselfAnimeTable, str]]]:
        """
        爬首頁的每週更新表。
        index 0 對應星期一。

        :param update: :class:`bool`是否更新動畫資訊(如果為否，則只會有名稱)。
        :param client: :class:`ClientSession`對話。
        :param from_cache: :class:`bool`是否從硬碟快取讀取。

        :return: :class:`list[list[tuple[MyselfAnimeTable, str]]]`(MyselfAnimeTable, 更新文字)
        """
        need_close = False if client else True
        client = client if client else new_session()
        while True:
            try:
                MYSELF_LOGGER.info(
                    f"Weekly Update: update:{update} from-cache:{from_cache}")
                # 取得網頁
                soup = await requests(
                    url=urljoin(MYSELF_URL, "portal.php"),
                    client=client,
                    soup=True,
                    from_cache=from_cache,
                    save_cache=True,
                    cache_delta=timedelta(days=1)
                )
                # 每周更新列表
                week_table = soup.select("#tabSuCvYn div.module.cl.xl.xl1")

                result: list[list[tuple[MyselfAnimeTable, str]]] = []
                tasks: list[Task] = []
                for tag in week_table:
                    # 每日更新列表
                    table_list = [(
                        MyselfAnimeTable(**{
                            "url": urljoin(MYSELF_URL, a_tag["href"]),
                            "name": a_tag.text
                        }),
                        a_tag.find_next("span").text.strip()
                    ) for a_tag in tag.select("a")]
                    # 新增至結果
                    result.append(table_list)
                    # 新增更新任務
                    tasks += list(map(
                        lambda data_tuple: create_task(
                            data_tuple[0].update(
                                client=client,
                                from_cache=from_cache
                            ),
                            name="Weekly Update Task"
                        ),
                        table_list
                    )) if update else []
                # 更新
                await gather(*tasks)
                # 檢查是否需要關閉連線
                if need_close:
                    await client.close()
                # 回傳
                return result
            except Exception as exc:
                exc_text = "".join(format_exception(exc))
                MYSELF_LOGGER.error("[Weekly Update]" + exc_text)
                await asleep(5)

    @staticmethod
    async def year_list(
        update: bool = False,
        client: Optional[ClientSession] = None,
        from_cache=True
    ) -> dict[str, list[MyselfAnimeTable]]:
        """
        取得年分列表頁面的動漫資訊。

        :param update: :class:`bool`是否更新動畫資訊(如果為否，則只會有名稱)。(備註:極度不建議設為True，不然他會把所有完結動畫頁面都爬過一次。)
        :param client: :class:`ClientSession`對話。
        :param from_cache: :class:`bool`是否從硬碟快取讀取。

        :return: :class:`dict[str, list[MyselfAnimeTable]]`{年分/季節: [MyselfAnimeTable]}
        """
        need_close = False if client else True
        client = client if client else new_session()
        while True:
            try:
                MYSELF_LOGGER.info(
                    f"Year List: update:{update} from-cache:{from_cache}")
                # 取得網頁
                soup = await requests(
                    url=urljoin(MYSELF_URL, "portal.php?mod=topic&topicid=8"),
                    client=client,
                    soup=True,
                    from_cache=from_cache,
                    save_cache=True,
                    cache_delta=timedelta(days=7)
                )
                # 每一季動畫列表
                season_table = soup.select(
                    "div.frame-tab.move-span.cl div.block.move-span")
                """
                div.frame-tab.move-span.cl 每一年的區塊
                div.block.move-span        每一季的區塊 
                """

                result: dict[str, list[MyselfAnimeTable]] = {}
                tasks: list[Task] = []
                for season in season_table:
                    # 每季列表
                    season_list = [
                        MyselfAnimeTable(**{
                            "url": urljoin(MYSELF_URL, a_tag["href"]),
                            "name": a_tag["title"]
                        })
                        for a_tag in season.select("a")
                    ]
                    # 新增至結果
                    result[
                        normalize(
                            UNICODE_CODE,
                            season.select_one("span.titletext").text
                        ).strip()
                    ] = season_list
                    # 新增更新任務
                    tasks += list(map(
                        lambda anime_table: create_task(
                            anime_table.update(
                                client=client,
                                from_cache=from_cache
                            ),
                            name="Year List Task"
                        ),
                        season_list
                    )) if update else []
                # 更新
                await gather(*tasks)
                # 檢查是否需要關閉連線
                if need_close:
                    await client.close()
                # 回傳
                return result
            except Exception as exc:
                exc_text = "".join(format_exception(exc))
                MYSELF_LOGGER.error(exc_text)
                await asleep(5)

    @staticmethod
    async def finish_list(
        start_page: int = 1,
        page_num: int = 10,
        update: bool = False,
        client: Optional[ClientSession] = None,
        from_cache=True
    ) -> list[MyselfAnimeTable]:
        """
        取得完結列表頁面的動漫資訊。

        :param start_page: :class:`int`開始的頁數。
        :param page_num: :class:`int`要抓的頁數。
        :param update: :class:`bool`是否更新動畫資訊(如果為否，則只會有名稱)。(備註:極度不建議設為True，不然他會把所有完結動畫頁面都爬過一次。)
        :param client: :class:`ClientSession`對話。
        :param from_cache: :class:`bool`是否從硬碟快取讀取。

        :return: :class:`list[MyselfAnimeTable]`
        """
        need_close = False if client else True
        client = client if client else new_session()
        start_page = max(1, int(start_page))
        page_num = max(1, int(page_num))
        while True:
            try:
                MYSELF_LOGGER.info(
                    f"Finish List: start-page:{start_page} page-num:{page_num} update:{update} from-cache:{from_cache}")
                # 取得網頁
                soup = await requests(
                    url=urljoin(MYSELF_URL, "forum-113-1.html"),
                    client=client,
                    soup=True,
                    from_cache=from_cache,
                    save_cache=True,
                    cache_delta=timedelta(days=7)
                )
                # 總頁數
                total_page_num = int(soup.select_one(
                    "label span")["title"].split(" ")[1])
                # 檢查起始頁數是否大於總頁數
                if (start_page > total_page_num):
                    return []
                # 更新爬取頁數
                page_num = min(page_num, total_page_num-start_page+1)

                # 頁面資料
                soup_list: list[BeautifulSoup] = []
                if start_page == 1:
                    soup_list.append(soup)
                    start_page += 1
                    page_num -= 1
                # 爬取所有目標頁面
                soup_task = [
                    create_task(
                        requests(
                            url=urljoin(
                                MYSELF_URL, f"forum-113-{page_index}.html"),
                            client=client,
                            soup=True,
                            from_cache=from_cache,
                            save_cache=True,
                            cache_delta=timedelta(days=7)
                        )
                    )
                    for page_index in range(start_page, start_page+page_num)
                ]
                soup_list += await gather(*soup_task)

                result: list[MyselfAnimeTable] = []
                tasks = []
                for soup in soup_list:
                    # 新增至結果
                    result += [
                        MyselfAnimeTable(**{
                            "url": urljoin(MYSELF_URL, a_tag["href"]),
                            "name": a_tag["title"],
                            "image-url": urljoin(MYSELF_URL, a_tag.select_one("img")["src"])
                        })
                        for a_tag in soup.select("ul.ml.mlt.mtw.cl div.c.cl a")
                    ]
                # 新增更新任務
                tasks += list(map(
                    lambda anime_table: create_task(
                        anime_table.update(
                            client=client,
                            from_cache=from_cache
                        ),
                        name="Finish List Task"
                    ),
                    result
                )) if update else []
                # 更新
                await gather(*tasks)
                # 檢查是否需要關閉連線
                if need_close:
                    await client.close()
                # 回傳
                return result
            except Exception as exc:
                exc_text = "".join(format_exception(exc))
                MYSELF_LOGGER.error(exc_text)
                await asleep(5)

    @staticmethod
    async def search(
        keyword: str,
        start_page: int = 1,
        page_num: int = 25,
        update: bool = False,
        client: Optional[ClientSession] = None,
        from_cache=True
    ) -> list[MyselfAnimeTable]:
        """
        搜尋動漫。

        :param keyword: :class:`str`關鍵字。
        :param start_page: :class:`int`開始搜尋的頁數。
        :param page_num: :class:`int`要抓的頁數。
        :param update: :class:`bool`是否更新動畫資訊(如果為否，則只會有名稱)。
        :param client: :class:`ClientSession`對話。
        :param from_cache: :class:`bool`是否從硬碟快取讀取。

        return: :class:`list[MyselfAnimeTable]`
        """
        need_close = False if client else True
        client = client if client else new_session()
        start_page = max(1, int(start_page))
        page_num = max(1, int(page_num))
        __query_list = [
            ("mod", "forum"),
            ("srchtxt", keyword),
            ("srchfid[]", 113),
            ("srchfid[]", 133),
            ("srchfid[]", 137),
            ("searchsubmit", "yes"),
        ]
        while True:
            try:
                MYSELF_LOGGER.info(
                    f"Search: keyword:{keyword} start-page:{start_page} page-num:{page_num} update:{update} from-cache:{from_cache}")
                redirect_url = (await requests(
                    url=urljoin(
                        MYSELF_URL, f"/search.php?{urlencode(__query_list)}"),
                    client=client,
                    raw=True
                )).url
                # 取得網頁
                soup = await requests(
                    url=f"{redirect_url}&page={start_page}",
                    client=client,
                    soup=True,
                    from_cache=from_cache,
                    save_cache=True,
                    cache_delta=timedelta(days=7)
                )
                # 總頁數
                total_result_num = int(soup.select_one(
                    "div.sttl em").text.split(" ")[-2])
                total_page_num = total_result_num // 20 + \
                    1 if total_result_num % 20 else total_result_num // 20
                # 檢查起始頁數是否大於總頁數
                if (start_page > total_page_num):
                    return []
                # 更新爬取頁數
                page_num = min(page_num, total_page_num-start_page+1)

                soup_list: list[BeautifulSoup] = []
                if start_page == 1:
                    soup_list.append(soup)
                    start_page += 1
                    page_num -= 1
                # 爬取所有目標頁面
                soup_task = [
                    create_task(
                        requests(
                            url=f"{redirect_url}&page={page_index}",
                            client=client,
                            soup=True,
                            from_cache=from_cache,
                            save_cache=True,
                            cache_delta=timedelta(days=7)
                        )
                    )
                    for page_index in range(start_page, start_page+page_num)
                ]
                soup_list += await gather(*soup_task)

                result: list[MyselfAnimeTable] = []
                tasks = []
                for soup in soup_list:
                    # 新增至結果
                    result += [
                        MyselfAnimeTable(**{
                            "url": f"thread-{parse_qs(unescape(a_tag['href']))['tid'][0]}-1-1.html",
                            "name": a_tag.text
                        })
                        for a_tag in soup.select("li.pbw a[href*=tid]")
                    ]
                # 新增更新任務
                tasks += list(map(
                    lambda anime_table: create_task(
                        anime_table.update(
                            client=client,
                            from_cache=from_cache
                        ),
                        name="Search List Task"
                    ),
                    result
                )) if update else []
                await gather(*tasks)
                if need_close:
                    await client.close()
                return result
            except Exception as exc:
                exc_text = "".join(format_exception(exc))
                MYSELF_LOGGER.error(exc_text)
                await asleep(5)
