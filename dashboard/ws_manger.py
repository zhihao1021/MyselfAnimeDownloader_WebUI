from asyncio import gather, create_task, sleep as asleep
from typing import Union, Any
from uuid import uuid1

from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed


class ConnectionManager:
    def __init__(self):
        # 所有WebSocket連接
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket) -> str:
        """
        將一個WebSocket加入列表。
        """
        # 等待連接
        await ws.accept()
        # 加入連接列表
        while (uuid := uuid1().hex) in self.active_connections.keys():
            await asleep(0.1)
        self.active_connections[uuid] = ws
        return uuid

    async def disconnect(self, uuid: str):
        """
        關閉WebSocket連接。
        """
        # 自連接列表移除
        if uuid in self.active_connections.keys():
            ws = self.active_connections[uuid]
            try:
                await ws.close()
            except:
                pass
            del self.active_connections[uuid]

    async def send(self, uuid: str, message: Union[str, bytes, Any]) -> bool:
        """
        發送訊息。
        """
        try:
            ws = self.active_connections[uuid]
            if type(message) == str:
                await ws.send_text(message)
            if type(message) == bytes:
                await ws.send_bytes(message)
            else:
                await ws.send_json(message)
            return True
        except (WebSocketDisconnect, ConnectionClosed):
            await self.disconnect(uuid)
            return False

    async def broadcast(self, message: Union[str, bytes, Any]):
        tasks = [
            create_task(self.send(uuid, message))
            for uuid in self.active_connections.keys()
        ]
        await gather(*tasks)
