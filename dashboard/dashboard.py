from configs import *

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
    
    @app.route("/api/")
    def api_():
        pass
