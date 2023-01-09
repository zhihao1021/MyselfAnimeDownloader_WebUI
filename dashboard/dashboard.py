from api import API
from configs import *
from modules import Json

from asyncio import new_event_loop

from flask import Flask, render_template, request
from eventlet import listen, wsgi

class Dashboard:
    app = Flask(__name__)
    def __init__(self) -> None:
        self.app.debug = WEB_DEBUG
        self.app.logger = WEB_LOGGER

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
        loop = new_event_loop()
        return loop.run_until_complete(API.search(data))

    # 下載
    @app.route("/api/download", methods=["POST", "GET"])
    def api_download():
        if request.is_json:
            data = request.get_json()
        else:
            return "", 400
        loop = new_event_loop()
        loop.run_until_complete(API.download(data))
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
        loop = new_event_loop()
        return loop.run_until_complete(API.get_week_anime())