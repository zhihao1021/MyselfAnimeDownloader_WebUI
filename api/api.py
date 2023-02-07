from anime_module import M3U8, Myself, MyselfAnime, MyselfAnimeTable
from configs import MYSELF_URL
from swap import VIDEO_QUEUE

from asyncio import gather, create_task
from pydantic import BaseModel, Field
from typing import Literal

class CacheData(BaseModel):
    from_cache: bool=Field(True, alias="from-cache")

class QueueModifyData(BaseModel):
    modify: Literal["pause", "resume", "stop", "upper", "lower", "highest", "lowest"]
    downloader_id: str=Field(alias="downloader-id")

class SearchData(CacheData):
    keyword: str

class DownloadData(BaseModel):
    episodes: list[MyselfAnime]


class GetFinishData(CacheData):
    page_index: int = Field(alias="page-index")


class API:
    @staticmethod
    def queue_modify(modify: Literal["pause", "resume", "stop", "upper", "lower", "highest", "lowest"], downloader_id: str):
        # 檢查是否為有效ID
        if downloader_id not in VIDEO_QUEUE.get_queue():
            return None
        downloader = VIDEO_QUEUE.get_downloader(downloader_id)

        # 辨認功能
        if modify == "pause":
            downloader.pause()
        elif modify == "resume":
            downloader.resume()
        elif modify == "stop":
            VIDEO_QUEUE.remove(downloader_id)
        elif modify == "upper":
            VIDEO_QUEUE.upper(downloader_id)
        elif modify == "lower":
            VIDEO_QUEUE.lower(downloader_id)
        elif modify == "highest":
            download_list = VIDEO_QUEUE.get_queue()
            download_list.remove(downloader_id)
            download_list.insert(0, downloader_id)
            VIDEO_QUEUE.update(download_list)
        elif modify == "lowest":
            download_list = VIDEO_QUEUE.get_queue()
            download_list.remove(downloader_id)
            download_list.append(downloader_id)
            VIDEO_QUEUE.update(download_list)
        return None

    @staticmethod
    def download_queue():
        def gen_data(downloader_id: str, downloader: M3U8):
            return {
                "name": f"{downloader.output_name} - {downloader.status()}",
                "progress": downloader.get_progress(),
                "status": downloader.status_code(),
                "order": VIDEO_QUEUE.get_index(downloader_id),
            }
        result = {
            downloader_id: gen_data(downloader_id, downloader)
            for downloader_id, downloader in VIDEO_QUEUE.get_data().items()
        }
        return result

    @staticmethod
    async def search(keyword: str, from_cache=True):
        if MYSELF_URL in keyword:
            # 如果搜尋連結
            anime_table = MyselfAnimeTable(**{"url": keyword})
            try:
                await anime_table.update(from_cache=from_cache)
                return {
                    "type": "anime",
                    "data": anime_table.dict()
                }
            except:
                pass
        search_result = await Myself.search(keyword, from_cache=from_cache)
        if len(search_result) == 1:
            anime_table = search_result[0]
            await anime_table.update()
            return {
                "type": "anime",
                "data": anime_table.dict()
            }
        return {
            "type": "search",
            "data": list(map(lambda anime_table: anime_table.dict(), search_result))
        }

    @staticmethod
    async def download(episodes: list[MyselfAnime]):
        tasks = [
            create_task(anime.gen_downloader())
            for anime in episodes
        ]

        downloaders = await gather(*tasks)
        for downloader in downloaders:
            VIDEO_QUEUE.add(downloader)
        return None

    @staticmethod
    async def get_week_anime(from_cache: bool = True):
        week_list = await Myself.weekly_update(from_cache=from_cache)
        result = list(map(
            lambda day_data: list(map(lambda day_data: (
                day_data[0].dict(), day_data[1]), day_data)),
            week_list
        ))
        return result

    @staticmethod
    async def get_year_anime(from_cache: bool = True):
        year_dict = await Myself.year_list(from_cache=from_cache)
        result = {
            key: list(map(lambda anime_table: anime_table.dict(), value))
            for key, value in year_dict.items()
        }
        return result

    @staticmethod
    async def get_finish_anime(page_index: int, from_cache: bool = True):
        finish_list = await Myself.finish_list(from_cache=from_cache, start_page=page_index, page_num=1)
        result = list(map(lambda anime_table: anime_table.dict(), finish_list))

        return result
