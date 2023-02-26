from aiorequests import Cache, url2cache_path
from api import API, CacheData, DownloadData, GetFinishData, QueueModifyData, SearchData, SettingUpdateData
from configs import CONFIG, GLOBAL_CONFIG, MYSELF_CONFIG, WEB_CONFIG
from swap import BROADCAST_WS, IMAGE_CACHE_QUEUE
from utils import ConnectionManager, Json

from os.path import isfile, join, split as ossplit

from aiofiles import open as aopen
from asyncio import sleep as asleep
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server
from websockets.exceptions import ConnectionClosed


def open_templates(filename: str):
    return join("dashboard/templates", filename)


download_queue = ConnectionManager()


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

    # 廣播訊息
    @app.websocket("/ws/broadcast")
    async def ws_broadcast(websocket: WebSocket):
        await BROADCAST_WS.connect(websocket)
        try:
            while True:
                await websocket.receive()
        except:
            await BROADCAST_WS.disconnect()

    # 下載列表
    @app.websocket("/ws/download-queue")
    async def ws_download_queue(websocket: WebSocket):
        uuid = await download_queue.connect(websocket)
        last_data = None
        while True:
            await asleep(1)
            data = API.download_queue()
            if data == last_data:
                continue
            last_data = data
            if not await download_queue.send(uuid, data):
                break

    # Root
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

    # 更新設定
    @app.post("/api/send-setting")
    async def api_send_setting(data: SettingUpdateData):
        GLOBAL_CONFIG.user_agent = data.user_agent
        GLOBAL_CONFIG.temp_path = data.temp_path
        GLOBAL_CONFIG.worker = data.worker
        GLOBAL_CONFIG.connections = data.conections
        MYSELF_CONFIG.dir_name = data.myself_dir
        MYSELF_CONFIG.file_name = data.myself_file
        MYSELF_CONFIG.download_path = data.myself_download
        MYSELF_CONFIG.check_update = data.myself_update

        CONFIG["global"] = GLOBAL_CONFIG
        CONFIG["myself"] = MYSELF_CONFIG
        await Json.dump("config.json", CONFIG)
        return "", 200

    # 取得每周更新列表
    @app.post("/api/get-week-anime", response_class=ORJSONResponse)
    async def api_get_week_anime(data: CacheData):
        return await API.get_week_anime(from_cache=data.from_cache)

    # 取得動畫年表
    @app.post("/api/get-year-anime", response_class=ORJSONResponse)
    async def api_get_year_anime(data: CacheData):
        return await API.get_year_anime(from_cache=data.from_cache)

    # 取得完結動畫列表
    @app.post("/api/get-finish-anime", response_class=ORJSONResponse)
    async def api_get_finish_anime(data: GetFinishData):
        return await API.get_finish_anime(
            page_index=data.page_index,
            from_cache=data.from_cache
        )

    # 取得檢查更新列表
    @app.get("/api/get-update-list", response_class=ORJSONResponse)
    async def get_update_list():
        if not isfile("update-list.txt"):
            return {
                "data": ""
            }
        async with aopen("update-list.txt") as update_file:
            content = await update_file.read()
            return {
                "data": content
            }

    # 修改檢查更新列表
    @app.post("/api/send-update-list")
    async def send_update_list(data: dict[str, str]):
        async with aopen("update-list.txt", mode="w") as update_file:
            await update_file.write(data.get("data", ""))
        return "", 200
