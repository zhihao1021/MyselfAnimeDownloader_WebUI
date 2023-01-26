from eventlet import listen, wsgi
from flask import Flask, render_template
from flask_socketio import SocketIO


class Dashboard:
    app = Flask(__name__)
    socket_io = SocketIO(app)
    def __init__(self) -> None:
        self.app.debug = True

    def run(self) -> None:
        wsgi.server(
            listen(("0.0.0.0", 80)),
            self.app,
        )

    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/include-html/<filename>")
    def include_html(filename):
        try: return render_template(filename)
        except: return ""

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
