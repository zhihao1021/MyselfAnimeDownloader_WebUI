VERSION = "Release 1.0"

from aiorequests import requests
from configs import *
from dashboard import Dashboard
from utils import Thread
from time import sleep
from traceback import format_exception

from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy, new_event_loop
from platform import system
from psutil import net_if_addrs

async def check_update() -> None:
    MAIN_LOGGER.info("開始檢查更新...")
    try:
        _res = await requests("https://api.github.com/repos/AloneAlongLife/MyselfAnimeDownloader_WebUI/releases/latest", raw=True)
        _data: dict = await _res.json()
        _latest_version = _data.get("tag_name", VERSION).replace("_", " ")

        if _latest_version == VERSION:
            MAIN_LOGGER.info("當前版本為最新版。")
            return
        _update_content = await requests("https://raw.githubusercontent.com/AloneAlongLife/MyselfAnimeDownloader_WebUI/master/LatestUpdate.md")
        MAIN_LOGGER.warning(f"檢查到更新版本: {_latest_version}")
        MAIN_LOGGER.warning(f"檢查到更新內容:\n{_update_content.decode()}")
        MAIN_LOGGER.warning("更新下載連結: https://github.com/AloneAlongLife/TixCraft-Dev/releases/latest")
    except Exception as e:
        _mes = "".join(format_exception(e))
        MAIN_LOGGER.warning(f"檢查更新失敗，原因: {_mes}")

if __name__ == "__main__":
    if system() == "Windows": set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    MAIN_LOGGER.info(f"當前版本: {VERSION}")

    loop = new_event_loop()
    loop.run_until_complete(check_update())
    loop.close()

    dashboard = Dashboard()
    dashboard_thr = Thread(target=dashboard.run)
    dashboard_thr.start()

    if WEB_HOST == "0.0.0.0":
        MAIN_LOGGER.info(f"Start At: 127.0.0.1:{WEB_PORT}")
        for net in net_if_addrs().values():
            for sni in net:
                if sni.netmask == "255.255.255.0":
                    MAIN_LOGGER.info(f"Start At: {sni.address}:{WEB_PORT}")
    else:
        MAIN_LOGGER.info(f"Start At: {WEB_HOST}:{WEB_PORT}")

    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            exit()