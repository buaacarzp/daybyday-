# class FaceBaseInit:
#     '''
#     模型初始化
#     '''
#     def __init__(self):
#         print("FaceBaseInit")
#         self.model = "FaceBaseInit init model "
# class PoseBaseInit:
#     '''
#     初始化模型操作
#     '''
#     def __init__(self):
#         self.model = "PoseBaseInit init model "
#         print("PoseBaseInit")
import logging
from config import _WEB_SOCKET_PROTOCOL
logging.basicConfig(format="%(asctime)s,%(levelname)s,%(asctime)s,%(filename)s:%(lineno)s:%(message)s",
                    level=logging.INFO)
                    #ilename="logserver.log",filemode ="w",level=logging.DEBUG)
class FaceAlgorithm(object):
    '''
    Face的方法
    '''
    def __init__(self):
        # FaceBaseInit.__init__(self)
        print("FaceAlgorithm")
    def Face_detect_Prepare1001(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        '''
        return {}

    def Face_detect_start1002(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Face_detect_stop1003(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Face_detect_cutdown1004(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        '''
        return {}
class PoseAlgorithm(object):
    def __init__(self,cPushup):
        self.cparam = None
        self.cPushup = cPushup
        # PoseBaseInit.__init__(self)
        try:
            self.cPushup.init()
            logging.info("模型实例化完成")
        except Exception:
            logging.error("模型实例化失败")
    def Pose_Assessment_prepare2001(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        '''
        try:
            if not mode:
                self.Task = recv_dict["examine1"]
                self.CapturePath = recv_dict["CapturePath"]
                self.level = recv_dict["level"]
                self.duration = recv_dict["duration"]
                self.outputFile = "dfl.mp4"
                logging.info(f"prepare步骤完成：self.Task={self.Task},self.Cap={self.CapturePath},self.level={self.level},self.duration={self.duration}")
            else:
                self.Task = 'taskderandom'
                self.CapturePath = '0000.mp4'
                self.level = '5'
                self.duration = '200'
                self.outputFile = "dfl.mp4"
                logging.info(f"prepare步骤完成：self.Task={self.Task},self.Cap={self.CapturePath},self.level={self.level},self.duration={self.duration}")

        except:
            logging.error("prepare步骤json参数解析错误")

        return _WEB_SOCKET_PROTOCOL['PROTOCOL6']['send1']
    def Pose_Assessment_start2002(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        outputfile:等待合并，目前设置固定的
        RTSP:'rtsp://admin:123456@192.168.1.102:554/mpeg4cif', '5', '200', 'dfl.mp4', '0'
        LOCAL:'0000.mp4', '5', '200', 'dfl.mp4', '0'
        '''
        if not mode:
            file_name,difficulty_level,frameNum,outputFile,deviceId = self.CapturePath ,self.level,self.duration,self.outputFile,'0'
        else:
            file_name,difficulty_level,frameNum,outputFile,deviceId='0000.mp4', '5', '200', 'dfl.mp4', '0'
        
        self.cPushup.start(file_name,difficulty_level,frameNum,outputFile,deviceId)
        
        logging.info("start步骤已经开始:取视频数据放入队列")
        _WEB_SOCKET_PROTOCOL['PROTOCOL7']['send1']['JSON']['task'] = self.Task
        return _WEB_SOCKET_PROTOCOL['PROTOCOL7']['send1']
    def Pose_Assessment_start2222(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        '''
        i = 0
        while not self.cPushup.isTailed():
            self.cparam = self.cPushup.processAction()
            logging.info("i={},self.cparam={}".format(i,self.cparam))
            i+=1
            yield self.cparam
            # print("self.cparam=",self.cparam)
        # print("处理完的结果为:",self.cPushup.param_dict['count'], self.cPushup.param_dict['count_including_wrong'])
    def Pose_Assessment_stop2003(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        这里目前是算法处理完调用的，但是无法解决在发送2222报文的时候接受到2003报文
        如何在处理的的过程中去recv这需要去考虑下
        '''
        
        self.cPushup.stop()#实际是控制往队列里面存数据，不是让算法结束
        return _WEB_SOCKET_PROTOCOL['PROTOCOL8']['send1']
    def Pose_Assessment_cutdown2004(self,recv_dict,mode):
        '''
        input: dict
        output: dict
        我做的是不销毁模型，因为多用户调用还需要一段加载模型的时长,所以不作任何操作。
        '''
        return {}