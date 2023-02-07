VERSION = "Release 1.2"

from aiorequests import requests
from configs import logger_init
from dashboard import Dashboard
from logging import getLogger
from traceback import format_exception

from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy, new_event_loop
from platform import system

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
        MAIN_LOGGER.warning("更新下載連結: https://github.com/AloneAlongLife/TixCraft-Dev/releases/latest")
    except Exception as exc:
        exc_text = "".join(format_exception(exc))
        MAIN_LOGGER.warning(f"檢查更新失敗，原因: {exc_text}")

if __name__ == "__main__":
    if system() == "Windows":
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logger_init()
    MAIN_LOGGER.info(f"當前版本: {VERSION}")

    loop = new_event_loop()
    loop.run_until_complete(check_update())

    dashboard = Dashboard()
    dashboard.run()

    # if WEB_HOST == "0.0.0.0":
    #     MAIN_LOGGER.info(f"Start At: 127.0.0.1:{WEB_PORT}")
    #     for net in net_if_addrs().values():
    #         for sni in net:
    #             if sni.netmask == "255.255.255.0":
    #                 MAIN_LOGGER.info(f"Start At: {sni.address}:{WEB_PORT}")
    # else:
    #     MAIN_LOGGER.info(f"Start At: {WEB_HOST}:{WEB_PORT}")

    # while True:
    #     try:
    #         sleep(1)
    #     except KeyboardInterrupt:
    #         exit()