import websockets,asyncio
import config,Utils
async def send_msg(websocket,pid,msg):
    #这里可以修改需要发送的消息
    # pid = PROTOCOL["PROTOCOL2"]["receive"]['id']
    # dictcode = PROTOCOL["PROTOCOL2"]["receive"]['JSON']
    #传入id和dict,返回字节流
    msg2 = Utils.pack(pid,msg)
    await websocket.send(msg2)
async def _Debug(msg):
    print(msg)

async def recv_msg(websocket):
    msg = await websocket.recv()
    _ID, _LENDATA, _DICT_Str = Utils.decode_uppack(msg)
    print("客户端:服务端发送的数据已经解析完毕:",_ID, _LENDATA, _DICT_Str)


async def main_logic(ip):
    async with websockets.connect(ip) as websocket:
        for idx,jsonfile in sendmsg:
            await send_msg(websocket,idx,jsonfile)
            print(idx) #1002报文客户端发出去了，服务端没有将while将消息一直接收导致的
            await recv_msg(websocket)
if __name__ =="__main__":
    ip = 'ws://192.168.1.111:8080'
    PROTOCOL = config._WEB_SOCKET_PROTOCOL
    # sendmsg =#[[PROTOCOL["PROTOCOL2"]["receive"]['id'],PROTOCOL["PROTOCOL2"]["receive"]['JSON']],
                #[PROTOCOL["PROTOCOL3"]["receive"]['id'],PROTOCOL["PROTOCOL3"]["receive"]['JSON']],
                #[PROTOCOL["PROTOCOL4"]["receive"]['id'],PROTOCOL["PROTOCOL4"]["receive"]['JSON']],
                #[PROTOCOL["PROTOCOL5"]["receive"]['id'],PROTOCOL["PROTOCOL5"]["receive"]['JSON']],
    sendmsg =   [[PROTOCOL["PROTOCOL6"]["receive"]['id'],PROTOCOL["PROTOCOL6"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL7"]["receive"]['id'],PROTOCOL["PROTOCOL7"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL8"]["receive"]['id'],PROTOCOL["PROTOCOL8"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL9"]["receive"]['id'],PROTOCOL["PROTOCOL9"]["receive"]['JSON']]
                ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_logic(ip))
    # loop.run_forever()
