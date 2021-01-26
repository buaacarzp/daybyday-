import asyncio
import websockets
import config
import Utils
import argparse
from logic import LogicProtocol 
import sys 
sys.path.append("/home/jp/daybyday-/websockets-server/easytrtpost/")
# print
print(sys.path)
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

from pushup import *
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

async def _Debug(msg):
    print(msg)

async def main_logic(web_socket,path):
    while True:
        # try:
        msg = await LogicdueRecvmsg(web_socket)
        if msg:#阻塞的
            await send_msg(web_socket,msg) 
        else:
            print("服务端待发送数据异常!")
        # except websockets.exceptions.ConnectionClosedOK :
        #     # print("code 10000")
        #     ...
def pre_parsers(parser):
    parser.add_argument('-ip','--ip',type=str,help="input the ip address!")#,action="store_false")
    parser.add_argument('-port','--port',type=str,help="inputs the ip port!")#,action="store_false")
    args = parser.parse_args()
    assert (args.ip is not None and args.port is not None) , "\nError:Please input the ip and port!"
    return args.ip,args.port

parser = argparse.ArgumentParser(description="Websockets start ")
IP,PORT = pre_parsers(parser)
PROTOCOL = config._WEB_SOCKET_PROTOCOL
start_server = websockets.serve(main_logic, IP,PORT) #不需要加ws
file_name,difficulty_level,frameNum,outputFile,deviceId='0000.mp4', '5', '10000', 'dfl.mp4', '0'
# file_name = sys.argv[1]
# difficulty_level = sys.argv[2]
# frameNum = sys.argv[3]
# outputFile = sys.argv[4]
# deviceId = int(sys.argv[5])
iii = time.time()
cPushup = CNvPushup(file_name, difficulty_level, frameNum, outputFile, deviceId)
cPushup.init()
cPushup.start()
while not cPushup.isTailed():
    cparam = cPushup.processAction()
yyy = time.time()
# encode.encode_frames(cPushup.param_dict['video'], file_name, 20)
logger.info("{} {}", cPushup.param_dict['count'], cPushup.param_dict['count_including_wrong'])
logger.info("{}", cPushup.param_dict['total_list'])

cPushup.releaseSelf()

print("NOTE: websocket server is runing...")
Logic = LogicProtocol() #服务一开始就开始初始化模型

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()