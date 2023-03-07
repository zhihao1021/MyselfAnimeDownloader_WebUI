
from aiorequests import requests, new_session
from anime_module import MyselfAnimeTable
from dashboard import Dashboard
from configs import logger_init, MYSELF_CONFIG
from swap import VIDEO_QUEUE
from utils import format_exception, Thread

from asyncio import (all_tasks, CancelledError, create_task, gather,
                     sleep as asleep, new_event_loop)
from logging import getLogger
from os.path import isfile
from platform import system
from typing import Iterable

from aiofiles import open as aopen

VERSION = "Release 1.3"
MAIN_LOGGER = getLogger("main")


async def check_update() -> None:
    MAIN_LOGGER.info("開始檢查更新...")
    try:
        data: dict = await requests("https://api.github.com/repos/AloneAlongLife/MyselfAnimeDownloader_WebUI/releases/latest", json=True)
        latest_version = data.get("tag_name", VERSION).replace("_", " ")

        if latest_version == VERSION:
            MAIN_LOGGER.info("當前版本為最新版。")
            return
        update_content = await requests("https://raw.githubusercontent.com/AloneAlongLife/MyselfAnimeDownloader_WebUI/master/LatestUpdate.md")
        MAIN_LOGGER.warning(f"檢查到更新版本: {latest_version}")
        MAIN_LOGGER.warning(f"檢查到更新內容:\n{update_content.decode()}")
        MAIN_LOGGER.warning(
            "更新下載連結: https://github.com/AloneAlongLife/TixCraft-Dev/releases/latest")
    except Exception as exc:
        exc_text = "".join(format_exception(exc))
        MAIN_LOGGER.warning(f"檢查更新失敗，原因: {exc_text}")


def __thread_job():
    loop = new_event_loop()
    try:
        loop.create_task(check_myself_update())
        loop.run_forever()
    except SystemExit:
        for task in all_tasks(loop):
            task.cancel()
        loop.stop()
        loop.close()


async def check_myself_update():
    try:
        latest = {}
        client = new_session()
        while True:
            # 檢查sn檔是否存在
            if not isfile("update-list.txt"):
                await asleep(1)
                continue

            # 讀取內容
            MAIN_LOGGER.info("讀取更新列表。")
            async with aopen("update-list.txt") as sn_file:
                raw_content = await sn_file.read()
            sn_list = raw_content.strip().split("\n")
            sn_list = map(lambda sn_str: sn_str.split("#", 1)[0].strip(), sn_list)
            animes = [
                MyselfAnimeTable(url=sn_url)
                for sn_url in filter(lambda sn_str: sn_str, sn_list)
            ]
            # 取得資料
            MAIN_LOGGER.info("開始檢查動畫更新。")
            result = await gather(*map(
                lambda anime_table: create_task(
                    anime_table.update(client=client, from_cache=False)
                ), animes
            ), return_exceptions=True)
            pass_animes = filter(lambda res: not issubclass(type(res[1]), Exception), zip(animes, result))
            animes = map(lambda res: res[0], pass_animes)

            # 檢查更新
            need_download: Iterable[MyselfAnimeTable] = list(filter(lambda anime_table: len(
                anime_table.VIDEO_LIST) != latest.get(anime_table.URL, 0), animes))

            # 開始下載
            for anime_table in need_download:
                MAIN_LOGGER.info(f"開始下載: {anime_table.NAME}。")
                episode_num = len(anime_table.VIDEO_LIST)
                latest[anime_table.URL] = episode_num
                downloader = await anime_table.VIDEO_LIST[-1].gen_downloader()
                VIDEO_QUEUE.add(downloader)

            await asleep(60 * MYSELF_CONFIG.check_update)
    except CancelledError:
        await client.close()

if __name__ == "__main__":
    if system() == "Windows":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logger_init()
    MAIN_LOGGER.info(f"當前版本: {VERSION}")

    loop = new_event_loop()
    loop.run_until_complete(check_update())
    loop.close()

    thrad = Thread(target=__thread_job, name="Background Job")
    thrad.start()

    dashboard = Dashboard()
    dashboard.run()

    thrad.stop()
    thrad.join()
