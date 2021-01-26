1.CNvPushup继承basetyp中的构造方法，在basetype中根据后端给的：\
```
file_name = sys.argv[1]
difficulty_level = sys.argv[2]
frameNum = sys.argv[3]
outputFile = sys.argv[4]
deviceId = int(sys.argv[5])
```\
这几个参数：rtsp地址，困难度，视频镇数目（考核时长）当前摄像头id\
来初始化得到cPushup这个对象。
2.cPushup调用：
```
cPushup.init()
```
```
def init(self):
    bRet = 0
    try:
        # 对于视频文件，必须保证从producer创建/read开始到start的这段时间，没有其他耗时操作，防止读取完时队列还没开始存入。
        self.tpose = TPose()
        self.prod = Producer(self.derived_class_name, self.rtsp, self.outputfile)
        self.preconsumer = PreConsumer(self, 4)

        self.param_dict = self.init_param()
        bRet = 1
    except Exception as e:
        logger.error(e)
        bRet = 0
        # raise e
    return bRet
```
在该init方法中去得到一个self.tpose模型实例化对象，self.prod关于杜视频和写视频的实例化对象,在实例化Producer的时候，该类中的构造方法已经在读视频了。如下：
```
self.thr = threading.Thread(target=self.read)  # 开启线程读摄像头并将图像存入队列
```
3.cPushup.start():
```
def start(self):
    """前端手动按钮
    """
    bRet = 0
    try:
        self.prod.start(int(self.total_frame_num))
        bRet = 1
    except Exception as e:
        logger.error(e)
        bRet = 0
        # raise e
    return bRet

```
self.prod是Producer中的方法，在Producer中也有一个start方法：```
def start(self, frame_num):  # 手动的考核指令
    self.isstart = True
    self.totaltime = frame_num  # 队列开始存入
    # 开始时一般不存在队列不为空的情况
    # while not self.write_queue.empty():
    #     self.write_queue.get()
    while not self.frame_queue.empty():
        self.frame_queue.get()
```
该start是从队列中获取刚才读的视频，但是获取的照片没有用到？？？

4.cPushup.isTailed()
```python
def isTailed(self):
    # isstart队列写入开始
    if self.prod.isend and self.preconsumer.kp_queue.qsize() == 0 and self.prod.frame_queue.qsize() < self.preconsumer.stack_num:
        logger.info("isTailed -- > True")
        self.prod.write_moov_atom()
        return 1
    else:
        return 0
```
该方法是判断是否有写入视频的情况：
4.1.self.prodisend为True,这种情况是在Producer中的stop方法:？？？那又什么时候调用stop，绕来绕去没看懂
```
def stop(self):
    """停止frame_queue队列存入"""
    logger.info("调用producer.stop()")
    if self.isend:  # 4种情况（前端取消、2分钟结束、违停、异常）会调用stop，防二次调用
        return
    self.isend = True
```
4.2.`self.preconsumer.kp_queue.qsize()<self.preconsumer.stack_num`为True:队列当前都已经取完了数据了
如果满足上述情况，则开始写视频
5.cparam = cPushup.processAction()
5.1 `self.preconsumer.process()` 这self.stack_num堆叠是什么意思？？？
```
def process(self):
    if self.stack_num == 1:
        self.process_one()
    elif self.stack_num == 4:
        self.process_four()
    else:
        raise Exception("堆叠数量错误")
```
6.模型推理在哪里？

建议：
1.代码尽量简洁点，因为之前你是给c++提供一个类所以写的这么复杂，我不太好梳理，只能尝试下将cPushup作为我后端的一个类，但是考虑到我后端是用携程，而你的代码中用到了多线程，并且用到多进程，我看看能不能作，如果不能可以改为携程。




以俯卧撑为例：
cPushup = CNvPushup(file_name, difficulty_level, frameNum, outputFile, deviceId)

1. rtsp视频流地址
2. 考核等级（一般为5，暂时不用其他等级）
3. 考核时长（以帧数计，一般为2分钟，fps为20，总时长2400祯，目前考虑多录2s，即为2440帧）
4. 视频保存路径（/usr/local/tnkhxt/files/video/xxx.mp4）
5. GPU序号（已弃用但保留了相关接口，传整数0即可）