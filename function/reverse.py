import asyncio
import websockets

TOKEN = "napcat_token_070421"


async def handler(websocket):

    # 获取请求头
    auth = websocket.request.headers.get("Authorization")

    # 校验 token
    if auth != f"Bearer {TOKEN}":
        print("Token错误:", auth)

        await websocket.close()

        return

    print("NapCat 已连接")

    try:

        async for message in websocket:

            print("收到消息:")
            print(message)
            print("-" * 50)

    except websockets.ConnectionClosed:

        print("连接断开")


async def main():

    print("等待 ws://localhost:9001 主动连接...")

    server = await websockets.serve(
        handler,
        "0.0.0.0",
        9001
    )

    await server.wait_closed()


asyncio.run(main())