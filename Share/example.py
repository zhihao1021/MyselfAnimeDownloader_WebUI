from myself import Myself
from m3u8 import M3U8
from threading import Thread
from time import sleep
import asyncio

async def get_downloader():
    # 取得每周更新列表
    week_update = await Myself.weekly_update()

    # 選取星期一 第一部
    anime_table = week_update[0][0][0]

    # 抓取動畫資訊
    await anime_table.update()

    # 取得最新一集
    anime = anime_table.VIDEO_LIST[-1]

    # 取得M3U8資訊
    host, m3u8 = await anime.get_m3u8_url()

    downloader = M3U8(
        host,
        m3u8,
        "new",     # 檔案名稱
    ) # 產生一個下載器，並將輸出位置設置於`./download/new.mp4`
    
    return downloader

def thread_job(downloader: M3U8):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(downloader.download())

if __name__ == "__main__":
    # 取得下載器
    downloader = asyncio.run(get_downloader())

    # 為了能同時輸出進度，新增線程進行下載
    thread = Thread(target=thread_job, args=(downloader,))
    thread.start()

    # 輸出進度
    while downloader.get_progress() < 1:
        print(f"{format(downloader.get_progress() * 100, '.2f')}%", end="\r")
        sleep(0.1)
    print("Download Finish")
    # 等待合成完成
    thread.join()
