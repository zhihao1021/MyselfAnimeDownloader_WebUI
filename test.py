# from anime_module import Myself, M3U8

# from asyncio import new_event_loop, all_tasks
# from time import sleep
# from threading import Thread

# async def main():
#     res = await Myself.weekly_update()
#     anime_table = res[-1][-2][0]
#     await anime_table.update()
#     anime = anime_table.VIDEO_LIST[0]
#     _host, _file = await anime.get_m3u8_url()

#     downloader = M3U8(
#         _host,
#         _file,
#         "test"
#     )
#     return downloader

# loop = new_event_loop()
# downloader = loop.run_until_complete(main())

# Thread(target=loop.run_until_complete, args=(downloader.download(10),)).start()

# while True:
#     print(f"{format(downloader.get_progress() * 100, '.2f')}%", end="\r")
#     sleep(0.1)

from asyncio import new_event_loop, create_task, gather, sleep, get_running_loop, get_event_loop, all_tasks, CancelledError
from traceback import print_exception

async def test(i):
    try:
        await sleep(i * 10 + 1)
    # except CancelledError as e:
        # raise e
    except:
        await sleep(i * 10 + 1)
    if i == 0:
        loop = get_running_loop()
        tasks = all_tasks(loop)
        for task in tasks:
            print(task.get_name())
            print(task.__hash__())
            if task.get_name() == "D":
                task.cancel()

async def main():
    tasks = []
    for i in range(10):
        tasks.append(loop.create_task(test(i), name="D"))
    res = await gather(*tasks, return_exceptions=True)
    print(res)

loop = new_event_loop()
try:
    loop.run_until_complete(main())
except Exception as e:
    print_exception(e)

input("End")