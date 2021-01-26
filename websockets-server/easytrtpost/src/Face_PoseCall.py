class FaceBaseInit:
    '''
    模型初始化
    '''
    def __init__(self):
        print("FaceBaseInit")
        self.model = "FaceBaseInit init model "
class PoseBaseInit:
    '''
    初始化模型操作
    '''
    def __init__(self):
        self.model = "PoseBaseInit init model "
        print("PoseBaseInit")

class FaceAlgorithm(FaceBaseInit):
    '''
    Face的方法
    '''
    def __init__(self):
        FaceBaseInit.__init__(self)
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
class PoseAlgorithm(PoseBaseInit):
    def __init__(self):
        PoseBaseInit.__init__(self)
        print("PoseAlgorithm")
    def Pose_Assessment_prepare2001(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Pose_Assessment_start2002(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        return {}
    def Pose_Assessment_start2222(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
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