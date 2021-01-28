import asyncio
import websockets
import config
import Utils
import argparse
from logic import LogicProtocol 
import sys 
sys.path.append("/home/jp/daybyday-/websockets-server/easytrtpost")
# print(sys.path)
import time
from loguru import logger
import copy
import json

import numpy as np
import cv2
from pushup_begin_end_detection import *
from pushup_leg_detection import *
from pushup_arm_detection import *
from pushup_body_detection import *
from situp_leg_detection import get_mean_value
from draw_utils import *
from basetype import BaseType
import encode
from collections import Generator

from pushup import CNvPushup
import logging
# logger = logging.getLogger('mylogger')
# logger.setLevel(logging.INFO)
# fh = logging.FileHandler('./test.log')
# fh.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# formatter = logging.Formatter("%(asctime)s,%(levelname)s,%(asctime)s,%(filename)s:%(lineno)s:%(message)s")
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# logger.addHandler(fh)
# logger.addHandler(ch)
# logger.info("foobar")
logging.basicConfig(format="%(asctime)s,%(levelname)s,%(asctime)s,%(filename)s:%(lineno)s:%(message)s",
                    filename="/home/jp/daybyday-/websockets-server/easytrtpost/src/logserver.log",filemode ="w",level=logging.DEBUG)
#                     #level=logging.DEBUG)

'''
如何将Logic仅仅初始化一次
'''
async def LogicdueRecvmsg(web_socket):
    msg = await web_socket.recv()
    msgsend = await Logic.AnalysisProtocol(msg) #error
    return msgsend
    

async def recv_msg(web_socket):
    msg = await web_socket.recv()
    _ID, _LENDATA, _DICT_Str = Utils.decode_uppack(msg)
    print("server:客户端发送的数据已经解析完毕:",_ID, _LENDATA, _DICT_Str)

async def send_msg(web_socket,msg):
    '''
    pid:id
    msg:dict
    '''
    # pid = PROTOCOL["PROTOCOL2"]['send1']['id']
    # dictcode = PROTOCOL["PROTOCOL2"]['send1']['JSON']
    # msg = Utils.pack(pid,dictcode)
    await web_socket.send(msg)

async def main_logic(web_socket,path):
    while True:
        try:
            msg = await LogicdueRecvmsg(web_socket)
            if len(msg)>1 and isinstance(msg[1],Generator):#阻塞的
                await send_msg(web_socket,msg[0])
                for gen in msg[1]:
                    # await send_msg(web_socket,gen) 
                    await send_msg(web_socket,Utils.pack(msg[2],gen))#这里是模拟真实数据
            else:
                await send_msg(web_socket,msg)
        except websockets.exceptions.ConnectionClosedOK :...
            
        except :
            logging.info("服务器发送数据异常！")

def pre_parsers(parser):
    parser.add_argument('-ip','--ip',type=str,help="input the ip address!")#,action="store_false")
    parser.add_argument('-port','--port',type=str,help="inputs the ip port!")#,action="store_false")
    parser.add_argument('-debug','--debug',help="choose debug or release",action="store_true")
    args = parser.parse_args()
    assert (args.ip is not None and args.port is not None) , "\nError:Please input the ip and port!"
    return args
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Websockets start ")
    args = pre_parsers(parser)
    IP,PORT,DEBUG = args.ip,args.port,args.debug
    PROTOCOL = config._WEB_SOCKET_PROTOCOL
    start_server = websockets.serve(main_logic, IP,PORT) #不需要加ws
    cPushup = CNvPushup()
    Logic = LogicProtocol(cPushup,DEBUG) #服务一开始就开始初始化模型
    print("NOTE: websocket server is runing...")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    # rtsp://admin:123456@192.168.1.102:554/mpeg4cif