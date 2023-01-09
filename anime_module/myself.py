from async_io import requests, new_session
from configs import *
from modules import Json

from asyncio import sleep as a_sleep, create_task, gather
from os.path import split as ossplit
from traceback import format_exception
from typing import Optional
from urllib.parse import parse_qs, urlencode, urljoin

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from websockets.client import connect as ws_connect, WebSocketClientProtocol

_STRIP = " \"\n\r"
BAN_CHAR = "\\/:*?\"<>|"

def retouch_name(name: str) -> str:
    """
    避免不正當名字出現導致資料夾或檔案無法創建。
    name: :class:`str`
        輸入字串。

    return: :class:`str`
        修飾後字串。
    """
    for char in BAN_CHAR: name = name.replace(char, " ")
    return name.strip(_STRIP)

class MyselfAnime:
    EPS_NAME: str # 集數名稱
    TID: str      # 動畫ID
    VID: str      # 影片ID
    def __init__(self, episode_name: str, tid: str, vid: str) -> None:
        """
        Myself影片。

        episode_name: :class:`str`
            集數名稱。
        tid: :class:`str`
            動畫ID。
        vid: :class:`str`
            影片ID。
        """
        self.EPS_NAME = episode_name.strip(_STRIP)
        self.TID = tid.strip(_STRIP)
        self.VID = vid.strip(_STRIP)
    
    async def get_m3u8_url(self, _ws: Optional[WebSocketClientProtocol]=None) -> tuple[str, str]:
        """
        取得m3u8連結。

        return: :class:`tuple[str, str]`
            (m3u8主機位置, m3u8檔案位置)
        """
        need_close = False
        if _ws == None:
            _ws = await ws_connect(
                uri="wss://v.myself-bbs.com/ws",
                origin="https://v.myself-bbs.com",
                user_agent_header=UA,
                open_timeout=TIMEOUT,
            )
            need_close = True
        if self.VID.isdigit():
            await _ws.send(Json.dumps({"tid": self.TID, "vid": self.VID, "id": ""}))
        else:
            await _ws.send(Json.dumps({"tid": "", "vid": "", "id": self.VID}))
        _res = await _ws.recv()
        _data: dict = Json.loads(_res)

        m3u8_file = urljoin("https://", _data["video"])
        m3u8_server = ossplit(m3u8_file)[0]

        if need_close: await _ws.close()
        return m3u8_server, m3u8_file
    
    def __str__(self) -> str:
        _class_name = f"<{self.__module__}.MyselfAnime>"
        return f"<{_class_name} TID={self.TID} VID={self.VID} episode-name=\"{self.EPS_NAME}\">"
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, __o: object) -> bool:
        if type(__o) != self.__class__: return False
        try:
            if __o.TID != self.TID: return False
            if __o.VID != self.VID: return False
            return True
        except: return False

class MyselfAnimeTable:
    URL: str                      # 網址
    TID: str                      # ID
    NAME: str                     # 名稱
    ANI_TYPE: str                 # 類型
    PRE_DATE: str                 # 首播日期
    EPS_NUM: str                  # 播放集數
    AUTHOR: str                   # 作者
    OFFICIAL_WEB: str             # 官方網站
    REMARKS: str                  # 備註
    INTRO: str                    # 簡介
    IMAGE_URL: str                # 縮圖連結
    VIDEO_LIST: list[MyselfAnime] # 影片清單
    updated: bool = False         # 是否已經更新資料
    def __init__(self, url: str, *, name: Optional[str]=None) -> None:
        """
        Myself動畫資料。

        url: :class:`str`
            網址。
        name: :class:`str`
            在不更新的情形下指定名稱(用於列表)。
        """
        self.URL = url.strip(_STRIP)   # https://myself-bbs.com/thread-48821-1-1.html
        _page = url.split("/")[-1]     # thread-48821-1-1.html
        self.TID = _page.split("-")[1] # 48821
        if name != None:
            name = name.replace("\r", "")
            self.NAME = name.strip(_STRIP)

    async def update(self, _client: Optional[ClientSession]=None) -> None:
        """
        更新資料。
        """
        _res = await requests(self.URL, _client)
        _soup = BeautifulSoup(_res, features="html.parser")    # 網頁本體
        _info_list = _soup.select("div.info_info li")   # 資訊欄列表
        _anime_list = _soup.select("ul.main_list > li") # 動畫列表

        self.NAME = _soup.select_one("meta[name='keywords']")["content"].strip()
        self.ANI_TYPE     = _info_list[0].text.split(":", 1)[1].strip(_STRIP)
        self.PRE_DATE     = _info_list[1].text.split(":", 1)[1].strip(_STRIP)
        self.EPS_NUM      = _info_list[2].text.split(":", 1)[1].strip(_STRIP)
        self.AUTHOR       = _info_list[3].text.split(":", 1)[1].strip(_STRIP)
        self.OFFICIAL_WEB = _info_list[4].text.split(":", 1)[1].strip(_STRIP)
        self.REMARKS      = _info_list[5].text.split(":", 1)[1].strip(_STRIP)
        self.IMAGE_URL    = _soup.select_one("div.info_img_box img")["src"]
        self.INTRO        = _soup.select_one("#info_introduction_text").text.strip(_STRIP)

        self.VIDEO_LIST = []
        for _anime_block in _anime_list:
            _episode_name = _anime_block.select_one("a").text                         # 集數名稱
            _video_url = _anime_block.select_one("a[data-href*=myself]")["data-href"] # 播放連結
            _vid = ossplit(_video_url)[1]                                             # 取得VID
            self.VIDEO_LIST.append(MyselfAnime(_episode_name, self.TID, _vid))
        self.updated = True
    
    def __str__(self) -> str:
        _class_name = f"<{self.__module__}.MyselfAnimeTable>"
        data = [f"update={self.updated}",]
        if self.updated:
            data += [
                f"name=\"{self.NAME}\"",
                f"animate-type=\"{self.ANI_TYPE}\"",
                f"premiere-date=\"{self.PRE_DATE}\"",
                f"episode-num=\"{self.EPS_NUM}\"",
                f"author=\"{self.AUTHOR}\"",
                f"offical-website=\"{self.OFFICIAL_WEB}\"",
                f"remarks=\"{self.REMARKS}\"",
                f"img-url=\"{self.IMAGE_URL}\"",
                f"introduction=\"{self.INTRO}\"",
                f"video-list={self.VIDEO_LIST}"
            ]
        else:
            if hasattr(self, "NAME"): data.append(f"name={self.NAME}")
        _data_text = " ".join(data)
        return f"<{_class_name} TID={self.TID} URL=\"{self.URL}\" <{_data_text}>>"
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, __o: object) -> bool:
        if type(__o) != self.__class__: return False
        try:
            if __o.URL != self.URL: return False
            if __o.updated != self.updated: return False
            return True
        except: return False

class Myself:
    @staticmethod
    async def weekly_update(update: bool=False, _client: Optional[ClientSession]=None) -> list[list[tuple[MyselfAnimeTable, str]]]:
        """
        爬首頁的每週更新表。
        index 0 對應星期一。

        update: :class:`bool`
            是否更新動畫資訊(如果為否，則只會有名稱)。

        return: :class:`list[list[tuple[MyselfAnimeTable, str]]]`
            (MyselfAnimeTable, 更新文字)
        """
        need_close = False
        if _client == None:
            _client = new_session()
            need_close = True
        while True:
            try:
                _res = await requests(urljoin(MYSELF_URL, "portal.php"), _client)
                _soup = BeautifulSoup(_res, features="html.parser")           # 網頁主體
                _week_table = _soup.select("#tabSuCvYn div.module.cl.xl.xl1") # 每周更新列表

                result: list[list[tuple[MyselfAnimeTable, str]]] = []
                if update: tasks = []
                for _index, _tag in enumerate(_week_table, 0):
                    result.append([])
                    for _anime_tag in _tag.select("a"):
                        _anime_url = urljoin(MYSELF_URL, _anime_tag["href"])
                        _anime_name = _anime_tag.text.strip()
                        _update_text = _anime_tag.find_next("span").text.strip()

                        _anime_table = MyselfAnimeTable(_anime_url, name=_anime_name)
                        if update: tasks.append(
                            create_task(_anime_table.update(_client))
                        )
                        result[_index].append((
                            _anime_table,
                            _update_text
                        ))
                if update:
                    await gather(*tasks)
                if need_close: await _client.close()
                return result
            except Exception as _exc:
                _exc_text = "".join(format_exception(_exc))
                MYSELF_LOGGER.error(_exc_text)
                await a_sleep(5)

    @staticmethod
    async def year_list(update: bool=False, _client: Optional[ClientSession]=None) -> dict[str, list[MyselfAnimeTable]]:
        """
        取得年分列表頁面的動漫資訊。

        update: :class:`bool`
            是否更新動畫資訊(如果為否，則只會有名稱)。
            備註:極度不建議設為True，不然他會把所有完結動畫頁面都爬過一次。

        :return: :class:`dict[str, list[MyselfAnimeTable]]`
            {年分/季節: [MyselfAnimeTable]}
        """
        need_close = False
        if _client == None:
            _client = new_session()
            need_close = True
        while True:
            try:
                _res = await requests(urljoin(MYSELF_URL, "portal.php?mod=topic&topicid=8"), _client)
                _soup = BeautifulSoup(_res, features="html.parser")                            # 網頁主體
                _season_table = _soup.select("div.frame-tab.move-span.cl div.block.move-span") # 每一季動畫列表
                """
                div.frame-tab.move-span.cl 每一年的區塊
                div.block.move-span        每一季的區塊 
                """

                result: dict[str, list[MyselfAnimeTable]] = {}
                if update: tasks = []
                for _season in _season_table:
                    _season_title = _season.select_one("span.titletext").text
                    _season_list = []
                    for _anime_tag in _season.select("a"):
                        _anime_url = urljoin(MYSELF_URL, _anime_tag["href"])
                        _anime_name = _anime_tag.text.strip()

                        _anime_table = MyselfAnimeTable(_anime_url, name=_anime_name)
                        if update: tasks.append(
                            create_task(_anime_table.update(_client))
                        )
                        _season_list.append(_anime_table)

                    result[_season_title] = _season_list.copy()
                if update:
                    await gather(*tasks)
                if need_close: await _client.close()
                return result
            except Exception as _exc:
                _exc_text = "".join(format_exception(_exc))
                MYSELF_LOGGER.error(_exc_text)
                await a_sleep(5)
    
    @staticmethod
    async def finish_list(start_page: int=1, page_num: int=100, update: bool=False, _client: Optional[ClientSession]=None) -> list[MyselfAnimeTable]:
        """
        取得年分列表頁面的動漫資訊。

        start_page: :class:`int`
            開始的頁數。
        page_num: :class:`int`
            要抓的頁數。
        update: :class:`bool`
            是否更新動畫資訊(如果為否，則只會有名稱)。
            備註:極度不建議設為True，不然他會把所有完結動畫頁面都爬過一次。

        return: :class:`list[MyselfAnimeTable]`
        """
        need_close = False
        if _client == None:
            _client = new_session()
            need_close = True
        start_page = max(1, start_page)
        page_num = max(1, page_num)
        while True:
            try:
                _res = await requests(urljoin(MYSELF_URL, "forum-113-1.html"), _client)
                _soup = BeautifulSoup(_res, features="html.parser") # 網頁主體
                _total_page = int(_soup.select_one("label span")["title"].split(" ")[1])
                start_page = min(_total_page, start_page)
                page_num = min(page_num, _total_page - start_page + 1)

                _soup_list: list[BeautifulSoup] = []
                _res_task = []
                if start_page == 1:
                    _soup_list.append(_soup)
                    start_page += 1
                    page_num -= 1
                for _page_index in range(start_page, start_page + page_num):
                    _res_task.append(create_task(
                        requests(urljoin(MYSELF_URL, f"forum-113-{_page_index}.html"), _client)
                    ))
                if len(_res_task) != 0:
                    _res_results = await gather(*_res_task)
                    _soup_list += list(map(lambda _res: BeautifulSoup(_res, features="html.parser"), _res_results))

                result = []
                if update: tasks = []
                for _soup in _soup_list:
                    _anime_list = _soup.select("ul.ml.mlt.mtw.cl h3 a")
                    for _anime_tag in _anime_list:
                        _anime_url = urljoin(MYSELF_URL, _anime_tag["href"])
                        _anime_name = _anime_tag.text.strip()

                        _anime_table = MyselfAnimeTable(_anime_url, name=_anime_name)
                        if update: tasks.append(
                            create_task(_anime_table.update(_client))
                        )
                        result.append(_anime_table)
                if update:
                    await gather(*tasks)
                if need_close: await _client.close()
                return result
            except Exception as _exc:
                _exc_text = "".join(format_exception(_exc))
                MYSELF_LOGGER.error(_exc_text)
                await a_sleep(5)

    @staticmethod
    async def search(keyword: str, start_page: int=1, page_num: int=25, update: bool=False, _client: Optional[ClientSession]=None) -> list[MyselfAnimeTable]:
        """
        搜尋動漫。

        keyword: :class:`str`
            關鍵字。
        start_page: :class:`int`
            開始搜尋的頁數。
        page_num: :class:`int`
            要搜尋的頁數。
        update: :class:`bool`
            是否更新動畫資訊(如果為否，則只會有名稱)。

        return: :class:`list[MyselfAnimeTable]`
        """
        need_close = False
        if _client == None:
            _client = new_session()
            need_close = True
        start_page = max(1, start_page)
        page_num = max(1, page_num)
        while True:
            try:
                _query_list = [
                    ("mod", "forum"),
                    ("srchtxt", keyword),
                    ("srchfid[]", 113),
                    ("srchfid[]", 133),
                    ("srchfid[]", 137),
                    ("searchsubmit", "yes"),
                ]
                _raw_res = await requests(urljoin(MYSELF_URL, f"/search.php?{urlencode(_query_list)}"), _client, raw=True)
                _redirect_url = _raw_res.url
                _res = await requests(f"{_redirect_url}&page={start_page}", _client)
                _soup = BeautifulSoup(_res, features="html.parser") # 網頁主體
                _total_res = int(_soup.select_one("div.sttl em").text.split(" ")[-2])
                _total_page = _total_res // 20
                if _total_res % 20 != 0: _total_page += 1
                start_page = min(_total_page, start_page)
                page_num = min(page_num, _total_page - start_page + 1)

                _soup_list: list[BeautifulSoup] = []
                _res_task = []
                if start_page == 1:
                    _soup_list.append(_soup)
                    start_page += 1
                    page_num -= 1
                for _page_index in range(start_page, start_page + page_num):
                    _res_task.append(create_task(
                        requests(f"{_redirect_url}&page={_page_index}", _client)
                    ))
                if len(_res_task) != 0:
                    _res_results = await gather(*_res_task)
                    _soup_list += list(map(lambda _res: BeautifulSoup(_res, features="html.parser"), _res_results))

                result = []
                if update: tasks = []
                for _soup in _soup_list:
                    _anime_list = _soup.select("li.pbw a[href*=tid]")
                    for _anime_tag in _anime_list:
                        _anime_tid = parse_qs(_anime_tag["href"].replace("amp;", ""))["tid"][0]
                        _anime_url = urljoin(MYSELF_URL, f"thread-{_anime_tid}-1-1.html")
                        _anime_name = _anime_tag.text.strip()

                        _anime_table = MyselfAnimeTable(_anime_url, name=_anime_name)
                        if update: tasks.append(
                            create_task(_anime_table.update(_client))
                        )
                        result.append(_anime_table)
                if update:
                    await gather(*tasks)
                if need_close: await _client.close()
                return result
            except Exception as _exc:
                _exc_text = "".join(format_exception(_exc))
                MYSELF_LOGGER.error(_exc_text)
                await a_sleep(5)
