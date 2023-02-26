from asyncio import create_task, gather, run, set_event_loop_policy, WindowsSelectorEventLoopPolicy

async def main():
    tasks = [
        create_task(job(i))
        for i in range(20)
    ]
    r = await gather(*tasks, return_exceptions=True)
    pass_animes = filter(lambda res: not issubclass(type(res[1]), Exception), zip(range(20), r))
    animes = map(lambda res: res[0], pass_animes)
    print(list(animes))

async def job(i):
    if i == 10:
        raise RuntimeError
    return i

set_event_loop_policy(WindowsSelectorEventLoopPolicy())
run(main())