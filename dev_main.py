from anime_module import Myself, M3U8
from dashboard import Dashboard
from modules import Thread
from swap import VIDEO_QUEUE
from time import sleep

from asyncio import create_task, gather, set_event_loop_policy, WindowsSelectorEventLoopPolicy, new_event_loop
from platform import system

async def m3u8s():
    res = await Myself.weekly_update()
    anime_table = res[-1][-5][0]
    await anime_table.update()
    # print(anime_table)
    ds = []
    tasks = []
    for i in range(1):
        tasks.append(create_task(anime_table.VIDEO_LIST[i].get_m3u8_url()))
    res = await gather(*tasks)
    for i, _data in enumerate(res):
        ds.append(M3U8(*_data, f"test-{i}"))
        print(*_data)
    return ds

if __name__ == "__main__":
    if system() == "Windows": set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    dashboard = Dashboard()
    dashboard_thr = Thread(target=dashboard.run)
    dashboard_thr.start()

    # loop = new_event_loop()
    # ds: list[M3U8] = loop.run_until_complete(m3u8s())
    # for d in ds: VIDEO_QUEUE.add(d)

    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            exit()