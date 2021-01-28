import asyncio
from threading import Thread
import websockets
import asyncio
import websockets
import sys 
import logging
import argparse
logging.basicConfig(format="%(asctime)s,%(levelname)s,%(asctime)s,%(filename)s:%(lineno)s:%(message)s",
                    filename="/home/jp/daybyday-/websockets-server/easytrtpost/src/logserver.log",filemode ="w",level=logging.DEBUG)
#                     #level=logging.DEBUG)


async def main_logic(web_socket,path):
    while True:
        await web_socket.send("hello")
    

def pre_parsers(parser):
    parser.add_argument('-ip','--ip',type=str,help="input the ip address!")#,action="store_false")
    parser.add_argument('-port','--port',type=str,help="inputs the ip port!")#,action="store_false")
    parser.add_argument('-debug','--debug',type=bool,help="choose debug or release")#,action="store_false")
    args = parser.parse_args()
    assert (args.ip is not None and args.port is not None) , "\nError:Please input the ip and port!"
    return args
async def hander(loop,server):
    loop.run_until_complete(server)
    loop.run_forever()
async def recv(server):
    msg = await server.recv()
    print("--->msg:",msg)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Websockets start ")
    args = pre_parsers(parser)
    IP,PORT,DEBUG = args.ip,args.port,args.debug
    start_server = websockets.serve(main_logic, IP,PORT) #不需要加ws
    
    
    print("NOTE: websocket server is runing...")
    
    loop1 = asyncio.get_event_loop()
    loop2 = asyncio.new_event_loop()
    thread1 = Thread(target=hander,args = (start_server))
    thread2 = Thread(target=recv,args = (start_server))
    thread1.start()
    thread1.join()
    thread2.start()
    thread2.join()
    # loop1.run_until_complete(start_server)
    # loop1.run_forever()
    # rtsp://admin:123456@192.168.1.102:554/mpeg4cif
