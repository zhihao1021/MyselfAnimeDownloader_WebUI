from websocket import create_connection
from modules import Json

ws = create_connection(
    url="wss://v.myself-bbs.com/ws",
    header={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    },
    host="v.myself-bbs.com",
    origin="https://v.myself-bbs.com"
)
ws.send(Json.dumps({"tid": "48821", "vid": "001", "id": ""}))
print(ws.recv())