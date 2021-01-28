#!/usr/bin/env python3
import sys
import time
from loguru import logger
import copy
import json
import cv2
from snakerun_begin_end_detection import *
from draw_utils import *
from basetype import BaseType
import encode


class CNvSnakeRun(BaseType):

    def init_param(self):
        param = dict(
            fps=self.prod.fps,
            width=self.prod.rtsp_width,
            height=self.prod.rtsp_height,

            # print("考核等级：" + level)  # 1~5
            level=self.level,

            # total_count=[],  # 视频中可能有多次上下杠
            time_last=0,
            time_current=0,
            time_start=-1,
            time_end=-1,
            time_count_down=20,

            video=[],  # 保存标注后的视频
            state_total=[],  # 记录全部状态
            total_list=[],  # 记录全部动作
            wrong_dict=dict(),

            # updown=0,  # 记录相对运动，以点1作为参考
            updown_delta=0,  # 与前一帧点8的坐标变化

            KEYPOINTS=[],  # 记录腿伸直时的关键点作为基准
            k_origin=[],
            k_processed=[],

            foot_behind_line=1,

            begin_flag=-1,
            end_flag=-1,
            began=-1,
            ended=-1,
            begin_time=-1,
            end_time=-1,

            i=0,
            index_offset=-1,
            processed_num=np.ones((19,))*5
        )
        return param

    def update_wrong_dict(self, param, time_start, time_end, wrong_list):
        # if not os.path.exists('logs'):
        #     os.mkdir('logs')
        # if not os.path.exists('logs/wrong_list.json'):
        #     os.mknod('logs/wrong_list.json')
        #
        status = [0] if len(wrong_list) == 0 else wrong_list
        time_period = (time_start, time_end)
        param['wrong_dict'] = {'status': status, 'total': round(param['time_current'] / param['fps'], 1),
                               'count': round(param['time_current'] / param['fps'], 1), 'time': time_period, 'msg': ""}
        # print(param['wrong_dict'])
        # with open('logs/wrong_list.json', 'a+') as f:
        #     json.dump(param['wrong_dict'], f)
        #     f.write('\n')
        return param['wrong_dict']

    def put_text(self, param, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'time_current: ' + str(round(param['time_current'] / param['fps'], 1)) + 's' + "    Level " + str(
                        param['level']), (0, 15), font, 1.2/2, (255, 255, 0), 2)
        cv2.putText(frame, 'foot_behind_line: ' + str(param['foot_behind_line']), (0, 30), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'updown_delta: ' + str(param['updown_delta']), (0, 45), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_flag/end_flag: ' + str(param['begin_flag']) + str(param['end_flag']), (0, 105), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_time/end_time: ' + str(param['begin_time']) + str(param['end_time']), (0, 120), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'i: ' + str(param['i']), (0, 135), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'time_start/time_end: ' + str(param['time_start']) + str(param['time_end']), (0, 150), font, 1.0/2, (0, 0, 255), 2)

        return frame

    def process_one_frame(self, param, kp, frame):
        # print(param['i'])
        # keypoints = self.tpose.get_keypoints(frame)
        keypoints = kp

        if len(keypoints) != 0 and self.param_dict['index_offset'] == -1:
            self.param_dict['index_offset'] = self.param_dict['i']

        if len(keypoints) == 0:
            logger.debug("len(keypoints) == 0")
            if len(param['k_origin']) > 0 and len(param['k_processed']) > 0 and len(param['state_total']) > 0:
                param['k_origin'].append(copy.deepcopy(param['k_origin'][-1]))
                param['k_processed'].append(param['k_processed'][-1])
                param['state_total'].append(param['state_total'][-1])

                frame = draw_parts(param['k_processed'][-2], frame)
            return param, frame

        keypoints = keypoints[0]  # 返回3维，目标单人，只取2维，方便计算
        param['k_origin'].append(copy.deepcopy(keypoints))
        keypoints, param['processed_num'] = data_process(keypoints, param['k_origin'], param['k_processed'], param['height'], param['processed_num'])  # 可变对象是引用传递
        # # 8点在使用前需要用处理过的9/12点重新赋值，减小丢失的影响
        # keypoints[8] = copy.deepcopy([round((keypoints[9][0] + keypoints[12][0])/2), round((keypoints[9][1] + keypoints[12][1])/2), (keypoints[9][2] + keypoints[12][2])/2])
        param['k_processed'].append(keypoints)
        # param['keypoints'] = copy.deepcopy(keypoints)

        frame = draw_parts(keypoints, frame)  # 绘制渲染处理后的骨骼

        if is_foot_behind_line(keypoints) != -1:
            param['foot_behind_line'] = is_foot_behind_line(keypoints)
        if len(param['state_total']) > 1:
            param['updown_delta'] = points_distance(param['k_origin'][-1][8], param['k_origin'][-2][8])

        if is_begin(keypoints) != -1:
            param['begin_flag'] = is_begin(keypoints) and is_foot_behind_line(keypoints)
        # print(begin_flag)
        if is_end(keypoints) != -1:
            param['end_flag'] = is_end(keypoints) and is_foot_behind_line(keypoints)

        param['state_total'].append((param['foot_behind_line'], param['begin_flag'], param['end_flag'], param['updown_delta']))

        # 判定站立于起终点线，只会进入一次
        if len(param['state_total']) >= 5:
            if sum(x[1] == 1 for x in param['state_total'][-5:]) >= 3 and param['began'] == -1:
                param['began'] = 1
                param['begin_time'] = param['i'] - 3
                logger.info("检测到准备动作")

        if len(param['state_total']) >= 10:
            # 判定冲过起终点线，只会进入一次
            if sum(x[2] == 1 for x in param['state_total'][-5:]) >= 3 and param['ended'] == -1 \
                    and param['began'] == 1 and param['i'] - param['begin_time'] > 2*20:  # 开始后的前2秒不计结束
                param['ended'] = 1
                param['end_time'] = param['i'] - 3
                logger.info("检测到违停动作")

            if param['began'] == 1 and param['ended'] == -1 and param['time_end'] == -1:

                # print(sum(x[0] == 0 for x in param['state_total'][-10:]),
                #       sum(x[3] < -2 for x in param['state_total'][-10:]))
                # for x in param['state_total'][-10:]:
                #     print(x[3])
                if sum(x[1] == 0 for x in param['state_total'][-10:]) >= 3 \
                        and sum(x[3] > 2 for x in param['state_total'][-10:]) >= 5 and param['time_start'] == -1:
                    param['time_start'] = param['i'] - 3
                    logger.info("计时开始 {}", param['i'])

                if sum(x[2] == 1 for x in param['state_total'][-10:]) >= 3 \
                        and sum(x[3] > 2 for x in param['state_total'][-10:]) >= 5 \
                        and param['time_start'] != -1 and param['time_end'] == -1:
                    param['time_end'] = param['i'] - 5
                    logger.info("计时结束 {}", param['i'])
                
                # 防止计时结束后不退出
                if param['time_end'] != -1 and param['i'] - param['time_end'] > 3*20:
                    param['ended'] = param['i']

                if param['time_start'] != -1 and param['time_end'] == -1:
                    param['time_current'] = param['i'] - param['time_start']
                    if param['time_current'] % 20 == 0:
                        param['wrong_dict'] = self.update_wrong_dict(param, round(param['time_start'] / param['fps'], 1),
                                                                     round(param['time_end'], 1), [])
            if param['began'] == 1 and param['ended'] == 1:
                if param['time_start'] != -1 and param['time_end'] == -1:
                    param['time_end'] = param['i']
                param['wrong_dict'] = self.update_wrong_dict(param, round(param['time_start'] / param['fps'], 1),
                                                             round(param['time_end'] / param['fps'], 1), [-3])

        return param, frame

    def processAction(self):
        try:
            while True:
                if self.preconsumer.kp_queue.qsize() == 0:
                    if self.prod.isend and self.prod.frame_queue.qsize() < 4:
                        break

                # if self.prod.frame_queue.qsize() == 0:
                #     if self.prod.isend:
                #         print("prod isend True")
                #         break  # 队列为空、考核结束，跳出
                #     continue  # 队列消耗速度快于生产
                self.preconsumer.process()
                if self.preconsumer.kp_queue.empty():
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
                        return json.dumps({'status': [-3], 'total': self.param_dict['time_current'],
                                          'count': self.param_dict['time_current'], 'time': [0.0, 0.0], 'msg': "stopped due to unallowed motion"})  # 输出停止信息

                self.param_dict['wrong_dict'] = dict()
                self.param_dict, frame = self.process_one_frame(self.param_dict, kp, frame)
                frame = self.put_text(self.param_dict, frame)
                # self.param_dict['video'].append(frame)
                end = time.time()
                # print(self.param_dict['i'], end - start)
                logger.debug("{} {}", self.param_dict['i'], end - start)
                self.param_dict['i'] += 1

                if len(self.param_dict['wrong_dict']) != 0:  # 有完整动作时返回，否则每3s发空串
                    # print(type(self.param_dict['wrong_dict']['status']), self.param_dict['wrong_dict']['status'])
                    # if -3 in self.param_dict['wrong_dict']['status']:
                    #     print("-333333333333333333333333333333333")
                    #     if not self.prod.isend:  # 前端调取
                    #         self.prod.stop()  # 违停动作返回-3
                    return json.dumps(self.param_dict['wrong_dict'])
                elif self.param_dict['i'] % 60 == 0:
                    return ""
            return json.dumps({'status': [-1], 'total': round(self.param_dict['time_current'] / self.param_dict['fps'], 1),
                               'count': round(self.param_dict['time_current'] / self.param_dict['fps'], 1), 'time': [0.0, 0.0], 'msg': "over"})
        except Exception as e:
            logger.error(e)
            # raise e
            return json.dumps({'status': [-2], 'total': round(self.param_dict['time_current'] / self.param_dict['fps'], 1),
                               'count': round(self.param_dict['time_current'] / self.param_dict['fps'], 1), 'time': [0.0, 0.0], 'msg': str(e)})


if __name__ == '__main__':
    file_name = sys.argv[1]
    difficulty_level = sys.argv[2]
    frameNum = sys.argv[3]
    outputFile = sys.argv[4]
    deviceId = int(sys.argv[5])
    iii = time.time()
    cSnakeRun = CNvSnakeRun(file_name, difficulty_level, frameNum, outputFile, deviceId)
    cSnakeRun.init()

    sss = time.time()
    cSnakeRun.start()
    while not cSnakeRun.isTailed():
        cparam = cSnakeRun.processAction()
        # print(cparam)
    logger.info(cSnakeRun.param_dict['time_current'])
    # encode.encode_frames(cSnakeRun.param_dict['video'], file_name, 20)
    ttt = time.time()
    cSnakeRun.releaseSelf()
    print(ttt - sss)
