# API Reference

## 使用說明
詳細的使用辦法請直接看程式碼，註解我都有打~~打註解好累XD~~，底下這裡僅會提供基礎的範例。

## 注意事項
這一組套件用於非同步(Async)環境的，對於Python的非同步執行要有一定了解才能最大化運作效率，如果要用於一般同步執行，可以參考 @hgalytoby 寫的[專案](https://github.com/hgalytoby/MyselfAnimeDownloader)，裡面有提供一般用於同步環境的Myself Methods。

## Example
```python
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


```
