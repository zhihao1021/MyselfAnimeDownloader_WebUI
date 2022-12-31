from configs import *
from modules import Json
from swap import VIDEO_QUEUE

from eventlet import listen, wsgi
from flask import Flask, render_template
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
    
    @app.route("/include-html/<filename>")
    def include_html(filename):
        try: return render_template(filename)
        except: return ""
    
    @app.route("/api/download-queue")
    def api_download_queue():
        _queue_dict = VIDEO_QUEUE._downloader_dict
        _result = {}
        for _downloader_id, _downloader in _queue_dict.items():
            _result[_downloader_id] = {
                "name": f"{_downloader.output_name} - {_downloader.status()}",
                "progress": _downloader.get_progress()
            }
        return _result
