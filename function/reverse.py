import asyncio
import websockets

from .logger import get_logger

TOKEN = "napcat_token_070421"

logger = get_logger()


async def handler(websocket):

    auth = websocket.request.headers.get("Authorization")

    if auth != f"Bearer {TOKEN}":
        msg = f"Token 验证失败: {auth}"
        print(msg)
        logger.warning(msg)

        await websocket.close()

        return

    msg = "NapCat 反向 WS 已连接"
    print(msg)
    logger.info(msg)

    try:

        async for message in websocket:

            print("收到新消息:")
            print(message)
            print("-" * 50)
            logger.info(f"收到消息: {message}")

    except websockets.ConnectionClosed:

        msg = "连接已断开"
        print(msg)
        logger.warning(msg)


async def main():

    msg = "等待 NapCat 反向连接..."
    print(msg)
    logger.info(msg)

    server = await websockets.serve(
        handler,
        "0.0.0.0",
        9001
    )

    await server.wait_closed()


asyncio.run(main())