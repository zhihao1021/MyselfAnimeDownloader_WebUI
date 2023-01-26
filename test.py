from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import uvicorn

class Dashboard():
    app = FastAPI()

    @app.get("/")
    async def root():
        return HTMLResponse("Hello World")

async def main():
    # from modules import Json
    # Json.dumps({"a": 123, "b": [4, "5", 6]})
    # await Json.dump("temp", {"a": 123, "b": [4, "5", 6]})
    # Json.dump_nowait("temp", {"a": 123, "b": [4, "5", 6]})
    # await Json.load("temp")
    # Json.load_nowait("temp")
    from aiohttp import ClientSession
    async with ClientSession() as client:
        await client.get("http://example.com", data=None)

if __name__ == "__main__":
    from asyncio import run
    run(main())
    # from timeit import timeit
    # def badname(name = "1\\2/3:4*5?6\"7<8>9|10.11"):
    #     ban = r'\/:*?"<>|.'
    #     for i in ban:
    #         name = str(name).replace(i, ' ')
    #     return name.strip()
    # trantab = str.maketrans(r'\/:*?"<>|.', " " * 10)
    # def trans_badname(name="1\\2/3:4*5?6\"7<8>9|10.11"):
    #     return name.translate(trantab)
    # def filter_badname(name="1\\2/3:4*5?6\"7<8>9|10.11"):
    #     return " ".join(filter(lambda char: char not in r"\/:*?\"<>|.", name))
    # def filter_only(name="1\\2/3:4*5?6\"7<8>9|10.11"):
    #     return filter(lambda char: char not in r"\/:*?\"<>|.", name)
    # print(f"for loop: {timeit(badname, number=10**6)}s")
    # print(f"translate: {timeit(trans_badname, number=10**6)}s")
    # print(f"filter: {timeit(filter_badname, number=10**6)}s")
    # print(f"filter only: {timeit(filter_only, number=10**6)}s")
    # dashboard = Dashboard()

    # config = uvicorn.Config(dashboard.app, host="0.0.0.0", port=5001)
    # server = uvicorn.Server(config)
    # server.run()
from pydantic import BaseModel, Field, validator
from unicodedata import normalize
from typing import Optional

STRIP = " \"\n\r"
UNICODE_CODE = "NFKC"

class MyselfAnime(BaseModel):
    """
    Myself影片。

    :param episode_name: :class:`str`集數名稱。
    :param tid: :class:`str`動畫ID。
    :param vid: :class:`str`影片ID。
    """
    EPS_NAME: str=Field(alias="episode_name") # 集數名稱
    TID: Optional[str]=Field(alias="tid")               # 動畫ID
    VID: str=Field(alias="vid")               # 影片ID
    @validator("TID", "VID", always=True)
    def id_validator(cls, value: str):
        try:
            return value.strip(STRIP)
        except:
            return value
    @validator("EPS_NAME")
    def eps_name_validator(cls, value: str):
        return normalize(UNICODE_CODE, value).strip(STRIP)