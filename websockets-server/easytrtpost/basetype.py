import sys
import cv2
import queue
import time
from datetime import datetime
import re
import os
import json
from tpose import TPose
import encode
import numpy as np
from cal_utils import *
import subprocess
import threading
import copy
from loguru import logger


class BaseType:
    def __init__(self, rtsp="", level="", total_frame_num="", outputfile="", deviceId=0):
        self.rtsp = str(rtsp)
        self.level = int(level)
        self.total_frame_num = int(total_frame_num)
        self.outputfile = outputfile
        self.deviceId = deviceId

        self.derived_class_name = self.__class__.__name__  # 子类名
        self.rel = False  # 是否已执行releaseSelf
        self.tpose = None
        self.prod = None
        self.preconsumer = None  # 介于producer和consumer之间，合并4图处理
        self.param_dict = None
        self.proj_dir = os.path.expanduser("~/trt_pose/tasks/human_pose/")
        self.ip_str = self.get_ip_str()
        self.log_file = self.get_log_path()

        logger.remove()
        logger.add(sys.stdout, level="DEBUG", format='{time:YYYY-MM-DD HH:mm:ss} |{level}|{file}:{name}:{function}:{line}| ======== {message}', enqueue=True)
        logger.add(self.log_file, level="INFO", format='{time:YYYY-MM-DD HH:mm:ss} |{level}|{file}:{name}:{function}:{line}| ======== {message}', enqueue=True)
        logger.info("考核项目：{}   等级：{}    视频设备：{}    录像文件：{}",
                    self.derived_class_name, self.level, self.ip_str, self.outputfile)

    def get_ip_str(self):
        ip_str = re.findall("\\d+\\.\\d+\\.\\d+\\.\\d+", self.rtsp)
        if len(ip_str) != 0:
            ip_str = ip_str[0]
        else:
            ip_str = "not_rtsp_source"

        return ip_str

    def get_log_path(self):
        month_str = datetime.now().strftime("%Y%m")
        day_str = datetime.now().strftime("%Y%m%d")
        log_dir = os.path.join(self.proj_dir, "logs", month_str)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = day_str + "-" + self.ip_str + ".log"
        log_path = os.path.join(log_dir, log_file)
        if not os.path.exists(log_path):
            os.mknod(log_path)

        return log_path

    def __del__(self):
        self.releaseSelf()

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

    def init_param(self):
        return ...

    def update_wrong_dict(self, param, up_start, down_end, wrong_list):  # 俯卧撑、曲臂悬垂与这里的参数不同
        # if not os.path.exists('logs'):
        #     os.mkdir('logs')
        # if not os.path.exists('logs/wrong_list.json'):
        #     os.mknod('logs/wrong_list.json')
        #
        status = [0] if len(wrong_list) == 0 else wrong_list
        time_period = (up_start, down_end)
        param['wrong_dict'] = {'status': status, 'total': param['count_including_wrong'],
                               'count': param['count'], 'time': time_period, 'msg': ""}
        # with open('logs/wrong_list.json', 'a+') as f:
        #     json.dump(param['wrong_dict'], f)
        #     f.write('\n')
        return param['wrong_dict']

    def put_text(self, param, frame):
        return ...

    def process_one_frame(self, param, kp, frame):
        return ...

    def processAction(self):
        try:
            while True:
                if self.preconsumer.kp_queue.qsize() == 0:
                    if self.prod.isend and self.prod.frame_queue.qsize() < self.preconsumer.stack_num:
                        break

                # if self.prod.frame_queue.qsize() == 0:
                #     if self.prod.isend:
                #         print("prod isend True")
                #         break  # 队列为空、考核结束，跳出
                #     continue  # 队列消耗速度快于生产
                self.preconsumer.process()
                if self.preconsumer.kp_queue.qsize() == 0:
                    continue
                kp, frame = self.preconsumer.kp_queue.get()
                # self.prod.sp.stdin.write(frame.tostring())
                start = time.time()

                # ret, frame = self.__capture.read()
                # if not ret:
                #     print("读取视频完毕（{}帧）".format(
                #         self.param['i']))
                #     break
                # srcFrame = copy.deepcopy(frame)

                if self.param_dict['end_time'] != -1:
                    self.param_dict['time_count_down'] -= 1
                    if self.param_dict['time_count_down'] <= 0:
                        return json.dumps({'status': [-3], 'total': self.param_dict['count_including_wrong'],
                                          'count': self.param_dict['count'], 'time': [0.0, 0.0], 'msg': "stopped due to unallowed motion"})  # 输出停止信息
                
                self.param_dict['wrong_dict'] = dict()
                self.param_dict, frame = self.process_one_frame(self.param_dict, kp, frame)
                frame = self.put_text(self.param_dict, frame)
                # self.prod.sp.stdin.write(frame.tostring())
                # cv2.imshow("fff", frame)
                # if cv2.waitKey(1) == 27:
                #     break
                # self.param_dict['video'].append(frame)
                end = time.time()
                # print(self.param_dict['i'], end - start)
                logger.debug(self.param_dict['i'])

                self.param_dict['i'] += 1

                if len(self.param_dict['wrong_dict']) != 0:  # 有完整动作时返回，否则每3s发空串
                    # print(type(self.param_dict['wrong_dict']['status']), self.param_dict['wrong_dict']['status'])
                    # if -3 in self.param_dict['wrong_dict']['status']:
                    #     print("-333333333333333333333333333333333")
                    #     if not self.prod.isend:  # 前端调取
                    #         self.prod.stop()  # 违停动作返回-3
                    return json.dumps(self.param_dict['wrong_dict'])
                elif self.param_dict['i'] % (3*20) == 0:  # 每3s发空串，保持ws连接
                    return ""

            # 队列已不再写入，并且所有帧已处理完
            logger.info("所有帧处理完毕")
            # self.prod.write_moov_atom()
            return json.dumps({'status': [-1], 'total': self.param_dict['count_including_wrong'],
                               'count': self.param_dict['count'], 'time': [0.0, 0.0], 'msg': "frame queue process finished"})
        except Exception as e:
            logger.error(e)
            # raise e  # 调试需要关闭注释
            # self.prod.write_moov_atom()
            return json.dumps({'status': [-2], 'total': self.param_dict['count_including_wrong'],
                               'count': self.param_dict['count'], 'time': [0.0, 0.0], 'msg': str(e)})

    def isTailed(self):
        # isstart队列写入开始
        if self.prod.isend and self.preconsumer.kp_queue.qsize() == 0 and self.prod.frame_queue.qsize() < self.preconsumer.stack_num:
            logger.info("isTailed -- > True")
            # self.prod.write_moov_atom()
            return 1
        else:
            return 0

    def releaseSelf(self):
        if self.rel:
            return  # 防二次调用
        self.rel = True
        self.prod.clear()
        logger.info("releaseSelf")
        # print(self.param_dict['count'], self.param_dict['count_including_wrong'])
        # print(self.param_dict['total_list'])

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

    def stop(self):
        bRet = 0
        try:
            self.prod.stop()
            # self.prod.write_moov_atom()
            # encode.encode_frames(self.param_dict['video'], self.outputfile, self.prod.fps)
            bRet = 1
        except Exception as e:
            logger.error(e)
            bRet = 0
            # raise e
        return bRet


class PreConsumer:
    """从Producer的队列中获取帧，叠加合并以后检测处理，分离关键点并存入队列。

    """
    def __init__(self, basetype: BaseType, stack_num):
        self.basetype = basetype
        self.kp_queue = queue.Queue()  # 关键点队列
        self.rtsp_width = self.basetype.prod.rtsp_width
        self.rtsp_height = self.basetype.prod.rtsp_height
        self.stack_num = stack_num  # 叠加图像的数量

    def process(self):
        if self.stack_num == 1:
            self.process_one()
        elif self.stack_num == 4:
            self.process_four()
        else:
            raise Exception("堆叠数量错误")

    def process_one(self):
        if self.basetype.prod.frame_queue.qsize() > 0:
            frame = self.basetype.prod.frame_queue.get()
            framew = copy.deepcopy(frame)
            sss = time.time()
            keypoints = self.basetype.tpose.get_keypoints(frame)  # 包含所有人的坐标的列表，可能为空
            ttt = time.time()
            logger.debug("reference time: {}".format(ttt-sss))
            if len(keypoints) != 0:
                keypoints = select_kp(keypoints, self.rtsp_width, self.rtsp_height)
            else:
                pass  # keypoints仍旧为[]
            self.kp_queue.put((keypoints, framew))  # 同时存入关键点和未渲染的帧

    def process_four(self):
        if self.basetype.prod.frame_queue.qsize() >= 4:
            frame = [[], [], [], []]
            for i in range(4):
                frame[i] = self.basetype.prod.frame_queue.get()
            frames = np.vstack((np.hstack((frame[0], frame[1])), np.hstack((frame[2], frame[3]))))
            sss = time.time()
            keypoints = self.basetype.tpose.get_keypoints(frames)
            ttt = time.time()
            logger.debug("reference time: {}".format(ttt-sss))
            kp = [[], [], [], []]
            kp[0], kp[1], kp[2], kp[3] = self.split_keypoints(keypoints)
            for ii in range(4):
                self.kp_queue.put((kp[ii], copy.deepcopy(frame[ii])))
                # if len(kp[ii]) != 0:
                #     if kp[ii][0][1][0] < 0 or kp[ii][0][1][1] < 0:
                #         print(0)

    def split_keypoints(self, keypoints):
        kp = [[], [], [], []]
        if len(keypoints) != 0:
            for k in keypoints:
                region = self.compute_region(k)
                for i in range(19):
                    if region == 1:
                        break  # 位于左上区域，不需要再循环更改坐标
                    elif region == 2:
                        k[i][0] = k[i][0] - self.rtsp_width
                    elif region == 3:
                        k[i][1] = k[i][1] - self.rtsp_height
                    elif region == 4:
                        k[i][0] = k[i][0] - self.rtsp_width
                        k[i][1] = k[i][1] - self.rtsp_height
                    else:
                        pass  # 位于原点，无需改变坐标

                    if not (0 <= k[i][0] <= self.rtsp_width and 0 <= k[i][1] <= self.rtsp_height):  # 超出图像的点清0
                        k[i] = [0, 0, 0]

                if region == 1:
                    kp[0].append(k)
                elif region == 2:
                    kp[1].append(k)
                elif region == 3:
                    kp[2].append(k)
                elif region == 4:
                    kp[3].append(k)
                else:
                    pass
            for i in range(4):
                if len(kp[i]) != 0:
                    kp[i] = select_kp(kp[i], self.rtsp_width, self.rtsp_height)
                else:
                    pass  # kp[i]仍旧为[]

        return kp[0], kp[1], kp[2], kp[3]  # 4个区域，每个区域的kp[i]都是一个包含不多于一个人的坐标的列表

    def compute_region(self, keypoints):
        """计算点所在的区域

        :param keypoints:
        :return:
        """
        average_coordinate = []
        for i in range(19):
            if keypoints[i][2] > 0.05:
                average_coordinate.append(keypoints[i])
        mean = np.mean(np.array(average_coordinate), axis=0)
        region = 0
        if 0 <= mean[0] < self.rtsp_width and 0 <= mean[1] < self.rtsp_height:
            region = 1
        elif mean[0] >= self.rtsp_width and 0 <= mean[1] < self.rtsp_height:
            region = 2
        elif 0 <= mean[0] < self.rtsp_width and mean[1] >= self.rtsp_height:
            region = 3
        elif mean[0] >= self.rtsp_width and mean[1] >= self.rtsp_height:
            region = 4

        return region


class Producer:
    def __init__(self, exam_type, rtsp, outputfile):
        # self.rtsp = "rtsp://admin:admin12345@192.168.1.124/cam/realmonitor?channel=1&subtype=0"
        self.exam_type = exam_type  # 仅用于判断考核类型（引体向上、曲臂悬垂），以旋转图像
        self.rtsp = rtsp
        # self.write_queue = queue.Queue()
        self.frame_queue = queue.Queue()  # 处理队列只有在isstart之后才存入

        self.cap = cv2.VideoCapture(self.rtsp)
        # opencv获取摄像头失败只报warning
        if not self.cap.isOpened():
            logger.error("获取视频流错误")
            raise Exception("获取视频流错误")  # 抛出异常，init函数中捕获
        self.rtsp_width = int(self.cap.get(3)) if self.exam_type not in ["CNvPullup", "CNvOverHang"] else int(self.cap.get(4))
        self.rtsp_height = int(self.cap.get(4)) if self.exam_type not in ["CNvPullup", "CNvOverHang"] else int(self.cap.get(3))
        self.fps = 20

        # # 对图像resize处理
        # self.resize_width = 480 if self.exam_type not in ["CNvPullup", "CNvOverHang"] else 270
        # self.resize_height = 270 if self.exam_type not in ["CNvPullup", "CNvOverHang"] else 480

        self.isstart = False  # 倒计时开始，队列存入开始
        self.totaltime = 0  # 2分钟计时
        self.isend = False  # 队列写入结束
        # self.stoped = False #ProcessAction执行完成
        self.thr = threading.Thread(target=self.read)  # 开启线程读摄像头并将图像存入队列
        # self.thr.setDaemon(True)
        self.thr.start()
        # self.thw = threading.Thread(target=self.write)  # 写
        # self.thw.setDaemon(True)  #
        self.outputfile = outputfile
        self.sp = None
        self.is_written = False  # 是否已写入视频moov atom

        try:
            self.init_FFmpeg()
        except Exception as e:
            logger.error("初始化FFmpeg错误")
            logger.error(e)
            raise e

    def read(self):
        # read = 0
        while True:
            if not self.cap.isOpened():
                logger.info("cap.isOpened() == True而结束")
                if not self.isend:
                    self.stop()
                break
            if self.isend:  #
                logger.info("帧停止存队列isend --> True")
                break
            # 一直读但不一定放入队列
            if self.isstart or "rtsp" in self.rtsp:  # rtsp流直接读，视频文件等isstart才开始读
                ret, frame = self.cap.read()
            # read += 1
            if not self.isstart:  # 未开始，不存队列，循环等待
                continue
            if self.totaltime <= 0:
                logger.info("计时结束")
                if not self.isend:
                    self.stop()
                break
                # continue
            if not ret:  # 如果是视频文件，要保证先调用self.stop()之后再break
                logger.info("读取到空帧而结束")
                if not self.isend:
                    self.stop()
                    # print(read)
                break
            self.totaltime -= 1
            if self.exam_type in ["CNvPullup", "CNvOverHang"]:
                frame = cv2.rotate(frame, rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)
                # frame = np.rot90(frame)
            # frame = cv2.resize(frame, (self.resize_width, self.resize_height))
            self.sp.stdin.write(frame.tostring())
            self.frame_queue.put(frame)
            # self.write_queue.put(copy.deepcopy(frame))
            # self.write_queue.put(frame)
            logger.debug("totaltime:    {}", self.totaltime)

        if self.cap.isOpened():
            self.cap.release()
        self.write_moov_atom()
        logger.info("读取完毕")

    def start(self, frame_num):  # 手动的考核指令
        self.isstart = True
        self.totaltime = frame_num  # 队列开始存入
        # 开始时一般不存在队列不为空的情况
        # while not self.write_queue.empty():
        #     self.write_queue.get()
        while not self.frame_queue.empty():
            self.frame_queue.get()

    def clear(self):
        # if self.isend:
        #     return  # 防二次调用
        # self.isend = True
        self.thr.join()
        # self.thw.join()

    def stop(self):
        """停止frame_queue队列存入"""
        if self.isend:  # 4种情况（前端取消、2分钟结束、违停、异常）会调用stop，防二次调用
            return
        logger.info("调用producer.stop()")
        self.isend = True
        # self.thr.join()
        # self.totaltime = 0
        # 受调用时机的限制，停止的同时开始写视频
        # if not self.write_queue.empty():
        #     try:
        #         self.write()
        #         # self.thw.start()
        #     except Exception as e:
        #         print("写视频错误")
        #         print(e)
        #         raise e

    # 写视频
    def init_FFmpeg(self):
        # output = "test.mp4"
        ffmpeg = 'ffmpeg'
        output = self.outputfile
        dimension = '{}x{}'.format(int(self.rtsp_width), int(self.rtsp_height))

        command = [ffmpeg,
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-s', dimension,
                   '-pix_fmt', 'bgr24',  # OpenCV uses bgr format
                   '-r', str(self.fps),
                   '-i', '-',
                   '-an',
                   '-c:v', 'libx264',
                   '-preset', 'veryfast',
                   '-pix_fmt', 'yuv420p',
                   #    '-moov_size', '65535',
                   #    '-movflags', 'empty_moov+faststart',
                   # '-profile:v', 'baseline',
                   # '-level', '1.3',
                   # '-tune:v', 'none',
                   # '-crf', '23.0',
                   # '-b:v', '5000k',
                   output]

        self.sp = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=2 ** 12)

    # def write(self):
    #     while not self.write_queue.empty():
    #         frame = self.write_queue.get()
    #         # cv2.imshow("fff", frame)
    #         # if cv2.waitKey(1) & 0xFF == ord('q'):
    #         #     break
    #         self.sp.stdin.write(frame.tostring())
    #     self.sp.stdin.close()
    #     self.sp.stderr.close()
    #     self.sp.wait()

    def write_moov_atom(self):
        """写入视频moov atom，以防视频无法播放。
        几种需要调用的情况：前端结束、处理完队列、异常等。
        :return:
        """
        if not self.is_written:
            self.is_written = True
            self.sp.stdin.close()
            self.sp.stderr.close()
            self.sp.wait()
            logger.info("视频保存完毕")
