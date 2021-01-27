import asyncio
from threading import Thread
import websockets
import argparse
from subprocess import call 
# bob = [0]
# async def recv_msg(web_socket):
#     res = await web_socket.recv()
#     # ls = ['python','/home/jp/daybyday-/websockets-server/easytrtpost/interruptserver/test.py']
#     # call(ls)
#     return res 
# class A:
#     def __init__(self,web_socket) :
#         self.bob =[0]
#         self.web_socket = web_socket
#         self.th = Thread(target=self.longrecv_msg,args=())
#         self.th.start()
    
#     def __await__(self):
#         yield 
#     async def longrecv_msg(self):
#         #开启一个线程接受报文
#         # while 1:
#         msg = await self.web_socket.recv()
#         self.bob[0] = 1
#     async def send_msg(self,msg):
#         while 1:
#             await self.web_socket.send(msg)
#             if self.bob[0] ==1:
#                 break
#         print("while循环退出")
#         self.th.join()

            



# # def longrecv_msg(web_socket):
# #     while 1:
# #         res = web_socket.recv()
# #         print("res=",res)
# #         if res :
# #             bob[0] = 1 
# #             print(bob)
# #             break
# #     # ls = ['python','/home/jp/daybyday-/websockets-server/easytrtpost/interruptserver/test.py']
# #     # call(ls)
# #     return res 

# # async def send_msg(web_socket,msg):
    
# #     rr = Thread(target= longrecv_msg,args=(web_socket,))
# #     rr.start()
# #     print("while 循环已经开始")
# #     while 1:
# #         await web_socket.send('hello')
# #         if bob[0] ==1:
# #             break
# #         # await web_socket.send(msg)
# #     rr.join()
# #     print('while循环已经退出')

# def pre_parsers(parser):
#     parser.add_argument('-ip','--ip',type=str,help="input the ip address!")#,action="store_false")
#     parser.add_argument('-port','--port',type=str,help="inputs the ip port!")#,action="store_false")
#     args = parser.parse_args()
#     assert (args.ip is not None and args.port is not None) , "\nError:Please input the ip and port!"
#     return args.ip,args.port
    
# # async def main_logic(web_socket,ip):
# #     msg ="fuwuduan"
# #     await send_msg(web_socket,msg)
# #     # await recv_msg(web_socket)

# #     print('??????')
# async def main_logic(web_socket,ip):
#     a = A(web_socket)
#     await a.send_msg('hello')

# if __name__=="__main__":
#     parser = argparse.ArgumentParser(description="Websockets start ")
#     IP,PORT = pre_parsers(parser)
#     start_server = websockets.serve(main_logic, IP,PORT) #不需要加ws
#     print("server run")
#     asyncio.get_event_loop().run_until_complete(start_server)
#     asyncio.get_event_loop().run_forever()

    

