以俯卧撑为例：
cPushup = CNvPushup(file_name, difficulty_level, frameNum, outputFile, deviceId)

1. rtsp视频流地址
2. 考核等级（一般为5，暂时不用其他等级）
3. 考核时长（以帧数计，一般为2分钟，fps为20，总时长2400祯，目前考虑多录2s，即为2440帧）
4. 视频保存路径（/usr/local/tnkhxt/files/video/xxx.mp4）
5. GPU序号（已弃用但保留了相关接口，传整数0即可）

Note:
2021-1-27 
1.修改了逻辑，修改basetype类
2.添加后端正常关闭异常捕捉
3.尝试每次返回
```
def Pose_Assessment_start2222(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        while not self.cPushup.isTailed():
            self.cparam = self.cPushup.processAction()
            print("self.cparam=",self.cparam)
        print("处理完的结果为:",self.cPushup.param_dict['count'], self.cPushup.param_dict['count_including_wrong'])
        return {}
```
4.TUDO：姿态考核停止要能触发开始的停止，但是目前没有这么写
5.TUDO：添加logging写入正在运行的程序