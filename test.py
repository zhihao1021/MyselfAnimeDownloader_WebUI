# from datetime import datetime, timedelta, timezone

# from asyncio import new_event_loop
# from aiosqlite import connect

# TIMEZONE = timezone(timedelta(hours=8))

# async def main(url):
#     async with connect("data.db") as db:
#         async with db.cursor() as cursor:
#             await cursor.execute(
#                 "SELECT update_time FROM cache WHERE url=:url",
#                 {"url": url}
#             )
#             if await cursor.fetchone() != None:
#                 await cursor.execute(
#                     "UPDATE cache SET update_time=:update_time WHERE url=:url",
#                     {"update_time": datetime.now(TIMEZONE).isoformat(), "url": url}
#                 )
#             else:
#                 await cursor.execute(
#                     "INSERT INTO cache (url, update_time) VALUES (:url, :update_time)",
#                     {"update_time": datetime.now(TIMEZONE).isoformat(), "url": url}
#                 )
#         await db.commit()

# loop = new_event_loop()
# loop.run_until_complete(main("https://www.1keydata.com/tw/sql/sqlselechtml"))
# print("END")

# import requests

# origin = open("dashboard/static/fonts/Noto_Sans_TC/Noto Sans TC.css").read()

# for i in range(120):
#     if origin.find(f"/* [{i}] */") == -1: continue
#     url = f"https://fonts.gstatic.com/s/notosanstc/v26/-nF7OG829Oofr2wohFbTp9iFOkMQAewlpbGXhhyYs0QF3kPVyLylzU95vTq1Ltj5xQez1g.{i}.woff2"
#     # open(f"dashboard/static/fonts/Noto_Sans_TC.{i}.woff2", mode="wb").write(requests.get(url).content)
#     origin = origin.replace(url, f"Noto_Sans_TC.{i}.woff2")
# open("dashboard/static/fonts/Noto_Sans_TC/Noto Sans TC.css", mode="w").write(origin)

from anime_module import Myself
from asyncio import new_event_loop

async def main():
    print(await Myself.finish_list(1,1))

loop = new_event_loop()
loop.run_until_complete(main())

