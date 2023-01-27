from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import uvicorn

class Dashboard():
    app = FastAPI()

    @app.get("/")
    async def root():
        return HTMLResponse("Hello World")

def thr():
    from asyncio import new_event_loop
    loop = new_event_loop()
    loop.create_task(main())
    loop.create_task(main_2())
    loop.run_forever()
    print("S")

async def main():
    await job(1)

async def main_2():
    await job(2)

async def job(i):
    from asyncio import sleep as asleep
    for _ in range(3):
        await asleep(1)
        print(i)

if __name__ == "__main__":
    from asyncio import run
    # run(main())
    from threading import Thread
    t = Thread(target=thr)
    t.run()
    t.join()