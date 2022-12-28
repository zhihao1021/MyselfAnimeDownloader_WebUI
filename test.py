from asyncio import new_event_loop, create_task, gather, sleep as a_sleep
from time import sleep
from threading import Thread

class AsymcTest:
    def __init__(self) -> None:
        self.i = 0

    def thr_job(self):
        loop = new_event_loop()
        loop.run_until_complete(self.main())

    async def async_job(self):
        for _ in range(10):
            await a_sleep(1)
            self.i += 1

    async def main(self):
        tasks = []
        for _ in range(5):
            tasks.append(create_task(self.async_job()))
        await gather(*tasks)

test = AsymcTest()

Thread(target=test.thr_job).start()

while True:
    print(test.i)
    sleep(1.1)