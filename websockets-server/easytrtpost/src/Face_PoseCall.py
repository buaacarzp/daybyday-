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
    def Face_detect_Prepare1001(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}

    def Face_detect_start1002(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Face_detect_stop1003(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Face_detect_cutdown1004(self,recv_dict):
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
            print("模型实例化完成")
        except Exception:
            print("模型实例化失败")
    def Pose_Assessment_prepare2001(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        
        print("prepare步骤已经在init构造方法中完成")
        return {}
    def Pose_Assessment_start2002(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        file_name,difficulty_level,frameNum,outputFile,deviceId='0000.mp4', '5', '200', 'dfl.mp4', '0'
        #'rtsp://admin:123456@192.168.1.102:554/mpeg4cif', '5', '200', 'dfl.mp4', '0'
        self.cPushup.start(file_name,difficulty_level,frameNum,outputFile,deviceId)
        
        print("已经开始取数据")
        return {}
    def Pose_Assessment_start2222(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        i = 0
        while not self.cPushup.isTailed():
            self.cparam = self.cPushup.processAction()
            # print("i={},self.cparam={}".format(i,self.cparam))
            logging.info("i={},self.cparam={}".format(i,self.cparam))
            i+=1
            yield self.cparam
            # print("self.cparam=",self.cparam)
        # print("处理完的结果为:",self.cPushup.param_dict['count'], self.cPushup.param_dict['count_including_wrong'])
        return {}
    def Pose_Assessment_stop2003(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Pose_Assessment_cutdown2004(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}