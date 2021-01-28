import sys 
sys.path.append("../src")
from config import _WEB_SOCKET_PROTOCOL
import Utils
import Face_PoseCall
import asyncio
class LogicProtocol:
    '''
    Logic构造函数中初始化FaceAlgorithm子类，子类中初始化FaceBaseInit父类中的模型。
    '''
    def __init__(self,cPushup=None,cOverHang=None,cSitup=None,cPullup=None,cSnakeRun=None,DEBUG=True):
        self.Face_algorithm = Face_PoseCall.FaceAlgorithm()
        self.Pose_algorithm = Face_PoseCall.PoseAlgorithm(cPushup)#目前保留一个
        self.debug = DEBUG
    def __await__(self):
        yield
    async def AnalysisProtocol(self,recvMsg):
        '''
        该函数包括了对接受信息的处理
        返回即将要发送的数据包
        '''
        _ID, _LENDATA, _DICT_Str = Utils.decode_uppack(recvMsg)
        print("server:客户端发送的数据已经解析完毕:",_ID, _LENDATA, _DICT_Str)
        #人脸识别信令解析
        if _ID == 1001:
            algoresults = self.Face_algorithm.Face_detect_Prepare1001(_DICT_Str,self.debug)
            sendId = 1001
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        elif _ID ==1002:
            algoresults = self.Face_algorithm.Face_detect_start1002(_DICT_Str,self.debug)
            sendId = 1002
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        elif _ID ==1003:
            algoresults = self.Face_algorithm.Face_detect_stop1003(_DICT_Str,self.debug)
            sendId = 1003
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        elif _ID ==1004:
            algoresults = self.Face_algorithm.Face_detect_cutdown1004(_DICT_Str,self.debug)
            sendId = 0
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        #人体姿态信令解析
        elif _ID ==2001:
            algoresults = self.Pose_algorithm.Pose_Assessment_prepare2001(_DICT_Str,self.debug)
            sendId = 2001
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        elif _ID ==2002:
            #2002需要做特殊处理,这里的返回值有两个
            algoresults = self.Pose_algorithm.Pose_Assessment_start2002(_DICT_Str,self.debug)
            sendId = 2002
            _PACK_DATA = Utils.pack(sendId,algoresults)
            sendId = 2222
            # algoresults = self.Pose_algorithm.Pose_Assessment_start2222(_DICT_Str)
            Generate = self.Pose_algorithm.Pose_Assessment_start2222(_DICT_Str,self.debug)
            # for gen in Generate:
            #     _PACK_DATA2 = Utils.pack(sendId,algoresults)
            # return _PACK_DATA1,_PACK_DATA2
            return _PACK_DATA,Generate,sendId
        elif _ID ==2003:
            algoresults = self.Pose_algorithm.Pose_Assessment_stop2003(_DICT_Str,self.debug)
            sendId = 2003
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        elif _ID ==2004:
            algoresults = self.Pose_algorithm.Pose_Assessment_cutdown2004(_DICT_Str,self.debug)
            sendId = 0
            _PACK_DATA = Utils.pack(sendId,algoresults)
            return _PACK_DATA
        
    async def Connect_Error(self,idx):
        '''
        该函数用于主动发送消息打包
        '''
        if idx == 0:
            _PACK_DATA = Utils.pack(idx,{})
            return _PACK_DATA
        elif idx == 401:
            _PACK_DATA = Utils.pack(idx,{})
            return _PACK_DATA


    

        

        


    






    
        