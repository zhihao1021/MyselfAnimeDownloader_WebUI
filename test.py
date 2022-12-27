# from asyncio import new_event_loop

# async def main():
#     from async_io import requests
#     from aiohttp import ClientResponse
#     from myself import MyselfAnime

#     _anime = MyselfAnime("01", "46195", "001")
#     _host, _ = await _anime.get_m3u8_url()
#     print(_host)

#     res: ClientResponse = await requests(
#         # f"{_host}/720p_000.ts",
#         "https://vpx15.myself-bbs.com/vpx/46195/001/720p_000.ts",
#         raw=True,
#         headers={
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition GX-CN)"
#         },
#     )
#     print(res.status)

# if __name__ == "__main__":
#     [].append
#     loop = new_event_loop()
#     loop.run_until_complete(main())
#     input("End")


def func():
    data = []
    for i in range(1000):
        data.append(i)

def func_():
    data = []
    data_ = data.append
    for i in range(1000):
        data_(i)

from timeit import timeit

if __name__ == "__main__":
    print("append():", timeit(func, number=100000), "s")
    print("data_=append:", timeit(func_, number=100000), "s")

    