import websockets,asyncio
import config,Utils
async def send_msg(websocket,msg):
    #这里可以修改需要发送的消息
    pid = PROTOCOL["PROTOCOL2"]["receive"]['id']
    dictcode = PROTOCOL["PROTOCOL2"]["receive"]['JSON']
    #传入id和dict,返回字节流
    msg = Utils.pack(pid,dictcode)
    await websocket.send(msg)
async def _Debug(msg):
    print(msg)

async def recv_msg(websocket):
    msg = await websocket.recv()
    _ID, _LENDATA, _DICT_Str = Utils.decode_uppack(msg)
    print("客户端:服务端发送的数据已经解析完毕:",_ID, _LENDATA, _DICT_Str)

async def main_logic(ip):
    async with websockets.connect(ip) as websocket:
        await send_msg(websocket,None)
        await recv_msg(websocket)
if __name__ =="__main__":
    ip = 'ws://192.168.1.107:8080'
    PROTOCOL = config._WEB_SOCKET_PROTOCOL
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_logic(ip))
