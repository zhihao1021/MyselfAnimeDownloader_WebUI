# import asyncio
# from myself import Myself
# from timeit import timeit

# # async def func(lock: asyncio.Lock, i: int):
# #     if False not in map(lambda lock: lock.locked(), locks):
# #         await asyncio.sleep(0.5)
# #         continue
# #     print(f"Coro {i} Start!")
# #     await asyncio.sleep(3)
# #     print(f"Coro {i} End!")
# #     # await lock.release()
# #     return


# async def main():
#     await Myself.weekly_update(update=True)
#     # print("Start.")
#     # locks = []
#     # for _ in range(num):
#     #     locks.append(asyncio.Lock())
#     # for i in range(50):
#     #     if False not in map(lambda lock: lock.locked(), locks):
#     #         await asyncio.sleep(0.5)
#     #         continue
#     #     for lock in [_lock for _lock in locks if not _lock.locked()]:
#     #     await func("", i)
#     # print("All Finish.")
# # ('https://vpx06.myself-bbs.com/vpx/46195/001', 'https://vpx06.myself-bbs.com/vpx/46195/001/720p.m3u8')
# def time_it():
#     loop = asyncio.new_event_loop()
#     loop.run_until_complete(main())


# print(timeit(time_it, number=1))

# import asyncio
# import async_io

# from async_io import requests

# async def main():
#     print("start")
#     headers = {
#         "origin": "https://v.myself-bbs.com/",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition GX-CN)",
#         "sec-fetch-mode": "cors",
#     }
#     _res = await requests("https://vpx13.myself-bbs.com/vpx/46195/001/720p_000.ts", headers=headers)
#     print(_res)
#     print("finish")

# loop = asyncio.new_event_loop()
# loop.run_until_complete(main())
# input()

from requests import get

res = get("https://vpx13.myself-bbs.com/vpx/46195/001/720p_000.ts", headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition GX-CN)"}, stream=True)
print(res.status_code)