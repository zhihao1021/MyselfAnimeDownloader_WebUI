from anime_module import gen_dir_name, gen_file_name, M3U8, Myself, MyselfAnimeTable
from anime_module.myself import MyselfAnime
from configs import *
from swap import VIDEO_QUEUE

from asyncio import create_task, gather, get_event_loop, new_event_loop

from eventlet import listen, wsgi
from flask import Flask, render_template, request
from flask_socketio import SocketIO


class Dashboard:
    app = Flask(__name__)
    socket_io = SocketIO(app)
    def __init__(self) -> None:
        self.app.debug = WEB_DEBUG

    def run(self) -> None:
        wsgi.server(
            listen((WEB_HOST, WEB_PORT)),
            self.app,
            WEB_LOGGER
        )

    @app.route("/")
    def index():
        return render_template("index.html")
    
    # Include HTML
    @app.route("/include-html/<filename>")
    def include_html(filename):
        try: return render_template(filename)
        except: return "", 404
    
    # 對貯列進行操作
    @app.route("/api/queue-modify", methods=["POST", "GET"])
    def api_queue_modify():
        # 取得資料
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                "id": request.values.get("id"),
                "modify": request.values.get("modify"),
            }
        _downloader_id = data.get("id")
        _modify = data.get("modify")
        # 檢查是否為有效ID
        if _downloader_id not in VIDEO_QUEUE.get_queue(): return ""
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
        return "", 200
    
    # 取得貯列
    @app.route("/api/download-queue")
    def api_download_queue():
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
    
    # 搜尋
    @app.route("/api/search", methods=["POST", "GET"])
    def api_search():
        def map_animetable(animetable: MyselfAnimeTable):
            _result = animetable.__dict__
            for _index, _anime in enumerate(_result["VIDEO_LIST"]):
                _result["VIDEO_LIST"][_index] = _anime.__dict__
            return _result
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                "keyword": request.values.get("keyword"),
            }
        _keyword = data.get("keyword").strip()

        loop = new_event_loop()
        if MYSELF_URL in _keyword:
            # 如果搜尋連結
            _anime_table = MyselfAnimeTable(_keyword)
            try:
                loop.run_until_complete(_anime_table.update())
                _anime_dict = map_animetable(_anime_table)
                return {
                    "type": "anime",
                    "data": _anime_dict
                }
            except: pass
        _search_result = loop.run_until_complete(Myself.search(_keyword))
        _search_result = list(map(map_animetable, _search_result))
        return {
            "type": "search",
            "data": _search_result
        }

    # 下載
    @app.route("/api/download", methods=["POST"])
    def api_download():
        print(request.get_json())
        if request.is_json:
            data = request.get_json()
        else:
            return "", 400

        _ani_name = data["ani_name"]
        _episodes = data["episodes"]
        _tasks = []
        loop = new_event_loop()
        for _episode_data in _episodes:
            _tasks.append(MyselfAnime(
                _ani_name,
                _episode_data["tid"],
                _episode_data["vid"]
            ).get_m3u8_url())

        _m3u8s = loop.run_until_complete(gather(*_tasks))
        for _m3u8_info, _episode in zip(_m3u8s, _episodes):
            _eps_name = gen_file_name(_ani_name, _episode["eps_name"])
            _downloader = M3U8(
                *_m3u8_info,
                _eps_name,
                gen_dir_name(_ani_name)
            )
            VIDEO_QUEUE.add(_downloader)
        return "", 200