import asyncio
import websockets


# async def 
# 客户端主逻辑
async def main_logic():
    async with websockets.connect('ws://192.168.1.111:8080') as websocket:
        # await auth_system(websocket)
        await websocket.send("kehuduan")

asyncio.get_event_loop().run_until_complete(main_logic())
