from anime_module import Myself, M3U8, VideoQueue, MyselfAnimeTable

from asyncio import new_event_loop, all_tasks, gather, create_task
from time import sleep, time
from threading import Thread

async def main():
    res = MyselfAnimeTable("https://myself-bbs.com/thread-48872-1-1.html")
    await res.update()

    tasks = []
    for anime in res.VIDEO_LIST:
        tasks.append(create_task(anime.get_m3u8_url()))
    res = await gather(*tasks)
    print(res)

loop = new_event_loop()
loop.run_until_complete(main())
for task in all_tasks(loop):
    loop.run_until_complete(task)
    task.cancel()
loop.close()
