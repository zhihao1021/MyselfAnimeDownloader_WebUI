from anime_module import Myself, M3U8, VideoQueue

from asyncio import new_event_loop, all_tasks, gather, create_task
from time import sleep, time
from threading import Thread

async def main():
    res = await Myself.weekly_update()
    anime_table = res[-1][-5][0]
    await anime_table.update()

    ds = []
    tasks = []
    for i in range(4):
        anime = anime_table.VIDEO_LIST[i]
        tasks.append(create_task(anime.get_m3u8_url()))
    res = await gather(*tasks)
    i = 1
    for _host, _file in res:

        ds.append(M3U8(
            _host,
            _file,
            f"test-{i}"
        ))
        i += 1
        print(_host, _file)
    return ds

loop = new_event_loop()
ds: list[M3U8] = loop.run_until_complete(main())
vq = VideoQueue(2)

for d in ds:
    vq.add(d)

timer = time()
while True:
    try:
        prog = map(lambda x: f"{x.output_name} {format(x.get_progress() * 100, '.2f')}%", ds)
        print(f"{' '.join(prog)} {format(time() - timer, '.2f')}", end="\r")
        sleep(0.1)
    except KeyboardInterrupt: break
lis = vq.get_queue()
vq.upper(lis[2])
input("KK")
while True:
    try:
        prog = map(lambda x: f"{x.output_name} {format(x.get_progress() * 100, '.2f')}%", ds)
        print(f"{' '.join(prog)} {format(time() - timer, '.2f')}", end="\r")
        sleep(0.1)
    except KeyboardInterrupt: break
# downloader.pause()
# input("PAUSE")
# while True:
#     try:
#         print(f"{format(downloader.get_progress() * 100, '.2f')}%", end="\r")
#         sleep(0.1)
#     except KeyboardInterrupt: break
# downloader.resume()
# input("RESUME")
# while True:
#     print(f"{format(downloader.get_progress() * 100, '.2f')}%", end="\r")
#     sleep(0.1)

# from asyncio import new_event_loop, create_task, gather, sleep, get_running_loop, get_event_loop, all_tasks, CancelledError
# from traceback import print_exception
# from threading import Thread, Lock as TLock
# from asyncio import Lock

# from configs import *

# async def async_range(count):
#     for i in range(count):
#         yield(i)
#         await sleep(0.0)

# async def test():
#     async for i in async_range(10):
#         await sleep(1)
#         async with LOCK:
#             print(f"Hello {i}")

# async def lock_manger(tasks):
#     while list(map(lambda x: x.done(), tasks)).count(False) > 1:
#         if TLOCK.locked():
#             await LOCK.acquire()
#             while TLOCK.locked():
#                 await sleep(0.1)
#             LOCK.release()
#         await sleep(0.1)

# async def main():
#     tasks = []
#     for i in range(3):
#         tasks.append(loop.create_task(test()))
#     tasks.append(loop.create_task(lock_manger(tasks)))
#     res = await gather(*tasks, return_exceptions=True)
#     print(res)

# loop = new_event_loop()
# LOCK = Lock()
# TLOCK = TLock()

# Thread(target=loop.run_until_complete, args=(main(),)).start()

# loop_ = new_event_loop()
# input("K")
# TLOCK.acquire()
# input("KS")
# TLOCK.release()

# input("End")