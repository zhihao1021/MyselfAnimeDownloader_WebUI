# from anime_module import Myself, M3U8, VideoQueue, MyselfAnimeTable

# from asyncio import new_event_loop, all_tasks, gather, create_task
# from time import sleep, time
# from threading import Thread

# from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
# from platform import system

# if system() == "Windows": set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# async def main():
#     # res = MyselfAnimeTable("https://myself-bbs.com/thread-48872-1-1.html")
#     # await res.update()

#     # tasks = []
#     # for anime in res.VIDEO_LIST:
#     #     tasks.append(create_task(anime.get_m3u8_url()))
#     # res = await gather(*tasks)
#     st_time = time()
#     res = await Myself.finish_list(page_num=50)
#     print(len(res), time() - st_time)

# loop = new_event_loop()
# loop.run_until_complete(main())
# for task in all_tasks(loop):
#     loop.run_until_complete(task)
#     task.cancel()
# loop.close()

# from flask import Flask

# if __name__ == "__main__":
#     app = Flask(__name__)

#     @app.route("/hello_world")
#     def root():
#         return "Hello World"

#     app.run("0.0.0.0", 8080)

import requests

origin = open("dashboard/static/fonts/Noto_Sans_TC/Noto Sans TC.css").read()

for i in range(120):
    if origin.find(f"/* [{i}] */") == -1: continue
    url = f"https://fonts.gstatic.com/s/notosanstc/v26/-nF7OG829Oofr2wohFbTp9iFOkMQAewlpbGXhhyYs0QF3kPVyLylzU95vTq1Ltj5xQez1g.{i}.woff2"
    # open(f"dashboard/static/fonts/Noto_Sans_TC.{i}.woff2", mode="wb").write(requests.get(url).content)
    origin = origin.replace(url, f"Noto_Sans_TC.{i}.woff2")
open("dashboard/static/fonts/Noto_Sans_TC/Noto Sans TC.css", mode="w").write(origin)
