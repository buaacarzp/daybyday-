import websockets,asyncio
import config,Utils
from threading import Thread
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


async def main_logic(ip,thread_num):
    async with websockets.connect(ip) as websocket:
        for idx,jsonfile in sendmsg:
            jsonfile['information'] = f"线程{thread_num}"
            await send_msg(websocket,idx,jsonfile)
            print(idx) #1002报文客户端发出去了，服务端没有将while将消息一直接收导致的
            await recv_msg(websocket)
def sss(ip,thread_num):
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_logic(ip,thread_num))

if __name__ =="__main__":
    ip = 'ws://192.168.1.100:8080'
    PROTOCOL = config._WEB_SOCKET_PROTOCOL
    sendmsg =[[PROTOCOL["PROTOCOL2"]["receive"]['id'],PROTOCOL["PROTOCOL2"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL3"]["receive"]['id'],PROTOCOL["PROTOCOL3"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL4"]["receive"]['id'],PROTOCOL["PROTOCOL4"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL5"]["receive"]['id'],PROTOCOL["PROTOCOL5"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL6"]["receive"]['id'],PROTOCOL["PROTOCOL6"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL7"]["receive"]['id'],PROTOCOL["PROTOCOL7"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL8"]["receive"]['id'],PROTOCOL["PROTOCOL8"]["receive"]['JSON']],
                [PROTOCOL["PROTOCOL9"]["receive"]['id'],PROTOCOL["PROTOCOL9"]["receive"]['JSON']]
                ]
    thread_list = []
    for _ in range(100):
        thread_list.append(Thread(target=sss,args=(ip,_)))
    for thr in thread_list:
        thr.start()
    for thr in thread_list:
        thr.join()

    
    # loop.run_forever()