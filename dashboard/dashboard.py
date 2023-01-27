from aiorequests import Cache, requests
from api import API
from configs import WEB_CONFIG
from utils import Json
from swap import IMAGE_CACHE_QUEUE

from asyncio import new_event_loop
from io import BytesIO
from os.path import isfile, join, split as ossplit

from aiofiles import open as aopen
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, HTMLResponse
from uvicorn import Config, Server

def __templates(filename: str):
    return join("/dashboard/templates", filename)

class Dashboard:
    app = FastAPI(title=__name__)
    def __init__(self) -> None:
        self.config = Config(
            app=self.app,
            host=WEB_CONFIG.host,
            port=WEB_CONFIG.port,
            log_config=None
        )
        self.server = Server(config=self.config)

    def run(self) -> None:
        self.server.run()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        async with aopen(__templates("index.html")) as file:
            return await file.read()
    
    # Include HTML
    @app.get("/include-html/{filename}")
    async def include_html(filename: str):
        file_path = __templates(filename)
        if not isfile(file_path):
            return "", 404
        async with aopen(file_path) as file:
            return await file.read()
    
    # Image Cache
    @app.get("/image_cache")
    async def image_cache(url: str):
        _, filename = ossplit(url)
        if Cache.is_cached(url):
            res = await requests(url, from_cache=True)
            FileResponse()
            return Response(res, media_type="image/jpeg")
            loop.close()
            return send_file(
                BytesIO(res),
                mimetype='image/jpeg',
                as_attachment=False,
                download_name=_filename
            )
        else:
            IMAGE_CACHE_QUEUE.add_nowait(_url)
            return redirect(_url)
    
    # 對貯列進行操作
    @app.route("/api/queue-modify", methods=["POST", "GET"])
    def api_queue_modify():
        # 取得資料
        if request.is_json:
            data = request.get_json()
        else:
            data = request.values.to_dict()
        API.queue_modify(data)
        return "", 200
        
    # 取得貯列
    @app.route("/api/download-queue")
    def api_download_queue():
        return API.download_queue()
    
    # 搜尋
    @app.route("/api/search", methods=["POST", "GET"])
    def api_search():
        if request.is_json:
            data = request.get_json()
        else:
            data = request.values.to_dict()
        from_cache = data.get("from_cache", True)
        if type(from_cache) == str:
            if from_cache == "false": from_cache = False
            else: from_cache = True
        loop = new_event_loop()
        res = loop.run_until_complete(API.search(data, from_cache=from_cache))
        loop.close()
        return res

    # 下載
    @app.route("/api/download", methods=["POST", "GET"])
    def api_download():
        if request.is_json:
            data = request.get_json()
        else:
            return "", 400
        loop = new_event_loop()
        loop.run_until_complete(API.download(data))
        loop.close()
        return "", 200
    
    # 取得設定
    @app.route("/api/get-setting", methods=["POST", "GET"])
    def api_get_setting():
        _result = {
            "ua": UA,
            "temp-path": TEMP_PATH,
            "thrs": THRS,
            "cons": CONS,
            "myself-dir": MYSELF_DIR,
            "myself-file": MYSELF_FILE,
            "myself-download": MYSELF_DOWNLOAD,
            "myself-update": MYSELF_UPDATE
        }
        return _result
    
    # 更新設定
    @app.route("/api/send-setting", methods=["POST", "GET"])
    def api_send_setting():
        if request.is_json:
            data = request.get_json()
        else:
            data = request.values.to_dict()
        CONFIG["global"].update({
            "user-agent":  data.get("ua", UA),
            "temp_path":  data.get("temp-path", TEMP_PATH),
            "threads":  int(data.get("thrs", THRS)),
            "connections":  int(data.get("cons", CONS)),
        })
        CONFIG["myself"].update({
            "dir_name": data.get("myself-dir", MYSELF_DIR),
            "file_name": data.get("myself-file", MYSELF_FILE),
            "download_path": data.get("myself-download", MYSELF_DOWNLOAD),
            "check_update": int(data.get("myself-update", MYSELF_UPDATE)),
        })
        Json.dump("config.json", CONFIG)
        return "", 200
    
    # 取得每周更新列表
    @app.route("/api/get-week-anime", methods=["POST", "GET"])
    def get_week_anime():
        if request.is_json:
            data = request.get_json()
        else:
            data = request.values.to_dict()
        from_cache = data.get("from_cache", True)
        if type(from_cache) == str:
            if from_cache == "false": from_cache = False
            else: from_cache = True
        loop = new_event_loop()
        res = loop.run_until_complete(API.get_week_anime(from_cache=from_cache))
        loop.close()
        return res
    
    # 取得動畫年表
    @app.route("/api/get-year-anime", methods=["POST", "GET"])
    def get_year_anime():
        if request.is_json:
            data = request.get_json()
        else:
            data = request.values.to_dict()
        from_cache = data.get("from_cache", True)
        if type(from_cache) == str:
            if from_cache == "false": from_cache = False
            else: from_cache = True
        loop = new_event_loop()
        res = loop.run_until_complete(API.get_year_anime(from_cache=from_cache))
        loop.close()
        return res
    
    # 取得完結動畫列表
    @app.route("/api/get-finish-anime", methods=["POST", "GET"])
    def get_finish_anime():
        if request.is_json:
            data = request.get_json()
        else:
            data = request.values.to_dict()
        from_cache = data.get("from_cache", True)
        page_index = int(data.get("page_index", 1))
        if type(from_cache) == str:
            if from_cache == "false": from_cache = False
            else: from_cache = True
        loop = new_event_loop()
        res = loop.run_until_complete(API.get_finish_anime(from_cache=from_cache, page_index=page_index))
        loop.close()
        return res