from asyncio import run


async def main():
    from aiohttp import ClientSession
    client = ClientSession(
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0 (Edition GX-CN)"
        }
    )

    ws = await client.ws_connect(
        url="wss://v.myself-bbs.com/ws",
        origin="https://v.myself-bbs.com",
    )

    await ws.send_json({"tid": "", "vid": "", "id": "AgADzQsAAlRQEFc"})
    # await ws.send_bytes(b'{"tid":"","vid":"","id":"AgADzQsAAlRQEFc"}')

    print(await ws.receive_json())

    await ws.close()

    await client.close()


if __name__ == "__main__":
    run(main())
