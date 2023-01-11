from anime_module import gen_dir_name, gen_file_name, M3U8, Myself, MyselfAnime, MyselfAnimeTable
from configs import *
from swap import VIDEO_QUEUE

from asyncio import gather, create_task

class API:
    @staticmethod
    def queue_modify(data: dict):
        _downloader_id = data.get("id")
        _modify = data.get("modify")
        # 檢查是否為有效ID
        if _downloader_id not in VIDEO_QUEUE.get_queue(): return None
        _downloader = VIDEO_QUEUE.get_downloader(_downloader_id)

        # 辨認功能
        if _modify == "pause":
            _downloader.pause()
        elif _modify == "resume":
            _downloader.resume()
        elif _modify == "stop":
            VIDEO_QUEUE.remove(_downloader_id)
        elif _modify == "upper":
            VIDEO_QUEUE.upper(_downloader_id)
        elif _modify == "lower":
            VIDEO_QUEUE.lower(_downloader_id)
        elif _modify == "highest":
            _download_list = VIDEO_QUEUE.get_queue()
            _download_list.remove(_downloader_id)
            _download_list.insert(0, _downloader_id)
            VIDEO_QUEUE.update(_download_list)
        elif _modify == "lowest":
            _download_list = VIDEO_QUEUE.get_queue()
            _download_list.remove(_downloader_id)
            _download_list.append(_downloader_id)
            VIDEO_QUEUE.update(_download_list)
        return None

    @staticmethod
    def download_queue():
        _queue_list = VIDEO_QUEUE.get_queue()
        _queue_dict = VIDEO_QUEUE._downloader_dict
        _result = {}
        for _downloader_id, _downloader in _queue_dict.items():
            _downloader = VIDEO_QUEUE.get_downloader(_downloader_id)
            try: _index = _queue_list.index(_downloader_id)
            except ValueError: _index = -1
            _result[_downloader_id] = {
                "name": f"{_downloader.output_name} - {_downloader.status()}",
                "progress": _downloader.get_progress(),
                "status": _downloader.status_code(),
                "order": _index,
            }
        return _result
    
    @staticmethod
    async def search(data: dict, from_cache=True):
        def map_animetable(animetable: MyselfAnimeTable):
            _result = animetable.__dict__
            if animetable.updated:
                for _index, _anime in enumerate(_result["VIDEO_LIST"]):
                    _result["VIDEO_LIST"][_index] = _anime.__dict__
            return _result
        try:
            _keyword = data.get("keyword").strip()
        except:
            return {"type": "error"}

        if MYSELF_URL in _keyword:
            # 如果搜尋連結
            _anime_table = MyselfAnimeTable(_keyword)
            try:
                await _anime_table.update(from_cache=from_cache)
                _anime_dict = map_animetable(_anime_table)
                return {
                    "type": "anime",
                    "data": _anime_dict
                }
            except: pass
        _search_result = await Myself.search(_keyword, from_cache=from_cache)
        if len(_search_result) == 1:
            _anime_table = _search_result[0]
            await _anime_table.update(from_cache=from_cache)
            _anime_dict = map_animetable(_anime_table)
            return {
                "type": "anime",
                "data": _anime_dict
            }
        _search_result = list(map(map_animetable, _search_result))
        return {
            "type": "search",
            "data": _search_result
        }
    
    @staticmethod
    async def download(data: dict):
        _ani_name = data["ani_name"]
        _episodes = data["episodes"]
        _tasks = []

        for _episode_data in _episodes:
            
            _tasks.append(create_task(MyselfAnime(
                _ani_name,
                _episode_data["tid"],
                _episode_data["vid"]
            ).get_m3u8_url()))

        _m3u8s = await gather(*_tasks)
        for _m3u8_info, _episode in zip(_m3u8s, _episodes):
            _eps_name = gen_file_name(_ani_name, _episode["eps_name"])
            _downloader = M3U8(
                *_m3u8_info,
                _eps_name,
                gen_dir_name(_ani_name)
            )
            VIDEO_QUEUE.add(_downloader)
        return ""

    @staticmethod
    async def get_week_anime(from_cache=True):
        def map_animetable(animetable_tuple: tuple[MyselfAnimeTable, str]):
            animetable, update_text = animetable_tuple
            return (animetable.__dict__, update_text)

        _week_list = await Myself.weekly_update(from_cache=from_cache)

        _result = list(map(
            lambda _day_data: list(map(map_animetable, _day_data)),
            _week_list
        ))
        
        return _result

    @staticmethod
    async def get_year_anime(from_cache=True):
        def map_animetable(animetable: MyselfAnimeTable):
            return animetable.__dict__
        _year_dict = await Myself.year_list(from_cache=from_cache)

        _result = {}
        for _key, _value in _year_dict.items():
            _result[_key] = list(map(map_animetable, _value))
        
        return _result
    
    @staticmethod
    async def get_finish_anime(from_cache=True):
        def map_animetable(animetable: MyselfAnimeTable):
            return animetable.__dict__
        _finish_list = await Myself.finish_list(from_cache=from_cache)

        _result = list(map(map_animetable, _finish_list))
        
        return _result
    