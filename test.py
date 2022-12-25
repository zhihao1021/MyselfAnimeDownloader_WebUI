# import asyncio
# from myself import Myself
# from async_io import requests
# from requests import get
# from time import time_ns
# from aiohttp import ClientSession
# from websockets.client import connect as ws_connect
# from configs import UA, TIMEOUT
# from modules import Json
# from urllib.parse import urlunparse

# async def test():
#     timer = time_ns()
    
#     res = await Myself.search("1", start_page=24)
#     print(res)
#     # await res["2022年07月（夏）"][2].update()
#     # print(res["2022年07月（夏）"][2])
    
#     print((time_ns() - timer) * 10 ** -9)


# loop = asyncio.new_event_loop()
# loop.run_until_complete(test())
# loop.close()
# input("End")

from timeit import timeit
from hashlib import sha1

CASE = list(range(1000))

def func(x: int, y: int):
    # CPU-Bound
    sha1((str(x) * y).encode())

def func_for_loop():
    for i in range(len(CASE)):
        func(i, CASE[i])

def func_map(): map(func, range(len(CASE)), CASE)

def func_map_enu(): map(func, enumerate(CASE))

if __name__ == "__main__":
    print("for loop:", timeit(func_for_loop, number=10 ** 4), "s")
    # for loop: 34.88419339992106 s
    print("map", timeit(func_map, number=10 ** 7), "s")
    # map: 15.0609385003333577 s
    print("map + enumerate", timeit(func_map_enu, number=10 ** 7), "s")
    # map + enumerate: 12.320802200119942 s