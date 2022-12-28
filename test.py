from anime_module import Myself, M3U8

from asyncio import new_event_loop, all_tasks
from time import sleep
from threading import Thread

async def main():
    res = await Myself.weekly_update()
    anime_table = res[-1][-2][0]
    await anime_table.update()
    anime = anime_table.VIDEO_LIST[0]
    _host, _file = await anime.get_m3u8_url()

    downloader = M3U8(
        _host,
        _file,
        "test"
    )
    return downloader

loop = new_event_loop()
downloader = loop.run_until_complete(main())

Thread(target=loop.run_until_complete, args=(downloader.download(10),)).start()

while True:
    print(f"{format(downloader.get_progress() * 100, '.2f')}%", end="\r")
    sleep(0.1)

input("End")
