from aiorequests import Cache, url2cache_path
from api import API, CacheData, DownloadData, GetFinishData, QueueModifyData, SearchData
from configs import GLOBAL_CONFIG, MYSELF_CONFIG, WEB_CONFIG
from swap import IMAGE_CACHE_QUEUE

from os.path import isfile, join, split as ossplit

from aiofiles import open as aopen
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server


def open_templates(filename: str):
    return join("dashboard/templates", filename)


class Dashboard:
    app = FastAPI(title=__name__)
    app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

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
        async with aopen(open_templates("index.html"), mode="rb") as file:
            return await file.read()

    # Include HTML
    @app.get("/include-html/{filename}", response_class=HTMLResponse)
    async def include_html(filename: str):
        file_path = open_templates(filename)
        if not isfile(file_path):
            return "", 404
        async with aopen(file_path, mode="rb") as file:
            return await file.read()

    # Image Cache
    @app.get("/image-cache")
    async def image_cache(url: str):
        _, filename = ossplit(url)
        if Cache.is_cached(url):
            _, filepath = url2cache_path(url)
            return FileResponse(filepath, filename=filename, content_disposition_type="inline")
        await IMAGE_CACHE_QUEUE.add(url)
        return RedirectResponse(url)

    # 對貯列進行操作
    @app.post("/api/queue-modify")
    def api_queue_modify(data: QueueModifyData):
        # 取得資料
        API.queue_modify(
            modify=data.modify,
            downloader_id=data.downloader_id
        )
        return "", 200

    # 取得貯列
    @app.get("/api/download-queue", response_class=ORJSONResponse)
    def api_download_queue():
        return API.download_queue()

    # 搜尋
    @app.post("/api/search", response_class=ORJSONResponse)
    async def api_search(data: SearchData):
        return await API.search(
            keyword=data.keyword,
            from_cache=data.from_cache
        )

    # 下載
    @app.post("/api/download")
    async def api_download(data: DownloadData):
        await API.download(episodes=data.episodes)
        return "", 200

    # 取得設定
    @app.get("/api/get-setting", response_class=ORJSONResponse)
    def api_get_setting():
        result = {
            "ua": GLOBAL_CONFIG.user_agent,
            "temp-path": GLOBAL_CONFIG.temp_path,
            "thrs": GLOBAL_CONFIG.worker,
            "cons": GLOBAL_CONFIG.connections,
            "myself-dir": MYSELF_CONFIG.dir_name,
            "myself-file": MYSELF_CONFIG.file_name,
            "myself-download": MYSELF_CONFIG.download_path,
            "myself-update": MYSELF_CONFIG.check_update
        }
        return result

    """
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
    """

    # 取得每周更新列表
    @app.post("/api/get-week-anime", response_class=ORJSONResponse)
    async def get_week_anime(data: CacheData):
        return await API.get_week_anime(from_cache=data.from_cache)

    # 取得動畫年表
    @app.post("/api/get-year-anime", response_class=ORJSONResponse)
    async def get_year_anime(data: CacheData):
        return await API.get_year_anime(from_cache=data.from_cache)

    # 取得完結動畫列表
    @app.post("/api/get-finish-anime", response_class=ORJSONResponse)
    async def get_finish_anime(data: GetFinishData):
        return await API.get_finish_anime(
            page_index=data.page_index,
            from_cache=data.from_cache
        )
