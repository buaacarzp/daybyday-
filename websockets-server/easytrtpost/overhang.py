#!/usr/bin/env python3
import sys
import time
from loguru import logger
import copy
import json
import cv2
from pullup_begin_end_detection import *
from pullup_head_detection import *
from pullup_leg_detection import *
from pullup_arm_detection import *
from pullup_body_detection import *
from draw_utils import *
from basetype import BaseType
import encode


class CNvOverHang(BaseType):

    def init_param(self):
        param = dict(
            fps=self.prod.fps,
            width=self.prod.rtsp_width,
            height=self.prod.rtsp_height,

            # print("考核等级：" + level)  # 1~5
            level=self.level,

            # total_count=[],  # 视频中可能有多次上下杠
            # time_last=0,
            time_current=0,
            time_start=-1,
            time_end=-1,
            # time_count=0,

            video=[],  # 保存标注后的视频
            # state_total=[],  # 记录全部状态
            total_list=[],  # 记录全部动作
            wrong_dict=dict(),

            # updown=0,  # 记录相对运动，以点1作为参考
            updown_delta=0,  # 与前一帧点8的坐标变化

            state_total=[],  # 状态记录
            KEYPOINTS=[],  # 记录腿伸直时的关键点作为基准
            k_origin=[],
            k_processed=[],

            arm_length_list=[],  # 记录最近100帧的前臂长度
            arm_length=0,  # 前臂长度
            scale=0,
            leg_length_list=[],
            leg_length=0,

            nose_pass=0,
            head_pass=0,
            body_move=0,
            leg_swing=0,
            leg_bend=0,

            begin_flag=-1,
            end_flag=-1,
            began=-1,
            ended=-1,
            begin_time=-1,
            end_time=-1,
            time_count_down=20,
            up=-1,
            down=-1,

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
        cv2.putText(frame, 'nose_pass: ' + str(param['nose_pass']), (0, 30), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'head_pass: ' + str(param['head_pass']), (0, 45), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'body_move: ' + str(param['body_move']), (0, 60), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'leg_swing: ' + str(param['leg_swing']), (0, 75), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'leg_bend: ' + str(param['leg_bend']), (0, 90), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_flag/end_flag: ' + str(param['begin_flag']) + str(param['end_flag']), (0, 105), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_time/end_time: ' + str(param['begin_time']) + str(param['end_time']), (0, 120), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'i: ' + str(param['i']), (0, 135), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'time_start/time_end: ' + str(param['time_start']) + str(param['time_end']), (0, 150), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'updown_delta: ' + str(param['updown_delta']), (0, 175), font, 1.0/2, (0, 0, 255), 2)

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

        # 记录全局最大腿长
        if get_leg_length(keypoints) != -1:
            param['leg_length'] = get_leg_length(keypoints)
        # if len(param['leg_length_list']) > 100:
        #     param['leg_length_list'].pop(0)
        if len(param['leg_length_list']) != 0:
            # print(leg_length)
            if param['leg_length'] > max(param['leg_length_list']):
                # print('当前最大腿长', leg_length)
                param['KEYPOINTS'] = copy.deepcopy(keypoints)
                param['leg_length_list'].append(param['leg_length'])
        else:
            param['KEYPOINTS'] = copy.deepcopy(keypoints)
            param['leg_length_list'].append(param['leg_length'])

        # 获取比例尺
        if get_arm_length(keypoints) != -1:
            param['arm_length'] = get_arm_length(keypoints)
        param['arm_length_list'].append(param['arm_length'])
        if len(param['arm_length_list']) > 100:
            param['arm_length_list'].pop(0)
        if param['arm_length'] == max(param['arm_length_list']):
            # print(arm_length)
            param['scale'] = get_length_scale(keypoints[3], keypoints[4], 25)  # 前臂参考长度

        param['leg_state'] = is_leg_open(keypoints) or is_leg_swing(keypoints, param['KEYPOINTS'])
        # 获取各状态，否则沿用上一帧的状态
        if is_nose_pass(keypoints) != -1:
            param['nose_pass'] = is_nose_pass(keypoints)
        if is_head_pass(keypoints) != -1:
            param['head_pass'] = is_head_pass(keypoints)
        if is_body_move(keypoints, param['scale']) != -1:
            param['body_move'] = is_body_move(keypoints, param['scale'])
        if is_leg_swing(keypoints, param['KEYPOINTS']) != -1:
            param['leg_swing'] = is_leg_swing(keypoints, param['KEYPOINTS'])
        if is_leg_bend(keypoints) != -1 and is_leg_open(keypoints) != -1:
            param['leg_bend'] = is_leg_bend(keypoints) or is_leg_open(keypoints)
        x_pass = param['nose_pass'] if param['level'] == 1 else param['head_pass']

        if is_begin(keypoints) != -1:
            param['begin_flag'] = is_begin(keypoints)  # 上杠
        # print(begin_flag)
        if is_end(keypoints) != -1:
            param['end_flag'] = is_end(keypoints)  # 下杠

        if len(param['state_total']) > 1:
            param['updown_delta'] = round(param['k_processed'][-1][8][1] - param['k_processed'][-2][8][1])

        param['state_total'].append((param['nose_pass'], param['head_pass'], param['body_move'], param['leg_swing'],
                                     param['leg_bend'], x_pass, param['updown_delta'],
                                     param['begin_flag'], param['end_flag']))

        # 判定手臂举起，只会进入一次
        if len(param['state_total']) >= 5:
            if sum(x[7] == 1 for x in param['state_total'][-5:]) >= 3 and param['began'] == -1:
                param['began'] = 1
                param['begin_time'] = param['i'] - 3
                logger.info("检测到准备动作")

        if len(param['state_total']) >= 10:
            # print(sum(x[8] == 1 for x in param['state_total'][-10:]),
            #       param['ended'] == -1, param['began'] == 1,
            #       param['i'] - param['begin_time'] >= 3*20)
            
            # 判定手臂放下，只会进入一次
            if sum(x[8] == 1 for x in param['state_total'][-10:]) >= 7 and param['ended'] == -1 \
                    and param['began'] == 1 and param['i'] - param['begin_time'] > 2*20:  # 开始后的前2秒不计结束
                param['ended'] = 1
                param['end_time'] = param['i'] - 7
                logger.info("检测到违停动作")
        
            if param['began'] == 1 and param['ended'] == -1 and param['time_end'] == -1:

                wrong_list = []
                pause_flag = 0
                if param['time_start'] != -1 and param['time_end'] == -1:
                    param['time_current'] = param['i'] - param['time_start']
                # 处于杠面附近时，上杠/下杠时刻检测
                # print(sum(x[6] < -3 for x in param['state_total'][-10:]),
                #       sum(x[5] == 1 for x in param['state_total'][-10:]),
                #       sum(x[6] > 3 for x in param['state_total'][-10:]))

                # for x in param['state_total'][-20:]:
                #     print(x[6])
                # print(x[6] for x in param['state_total'][-20:])
                param['up'] = -1
                param['down'] = -1
                if is_pull_up(param['k_processed']):
                    param['up'] = 1
                if is_pull_down(param['k_processed']) and param['up'] == 1:
                    param['down'] = 1

                # print(param['i'], param['up'], param['down'], sum(x[5] == 1 for x in param['state_total'][-10:]))
                if param['down'] == 1 and sum(x[5] == 0 for x in param['state_total'][-10:]) >= 3:  # 最近10帧，防止振荡。杠下状态。
                    if param['time_start'] != -1:  # 已开始检测
                        if param['time_end'] == -1:  # 而未结束
                            logger.info("计时结束")
                            param['time_end'] = param['i'] - 3
                        param['time_current'] = param['time_end'] - param['time_start']

                        pause_flag = 1  # 1/2级
                        if param['level'] == 1:
                            wrong_list.append(210)
                        else:
                            wrong_list.append(210)
                            wrong_list.append(220)

                if param['up'] == 1 and sum(x[5] == 1 for x in param['state_total'][-10:]) >= 3:  # 杠上状态
                    if param['time_start'] == -1:  # 未开始检测
                        logger.info("计时开始")
                        param['time_start'] = param['i'] - 3
                        param['time_current'] = param['i'] - param['time_start']
                        # 只在开始时汇报一次
                        param['wrong_dict'] = self.update_wrong_dict(param, round(param['time_start'] / param['fps'], 1),
                                                                     round(param['time_end'] / param['fps'], 1), [])

                if param['level'] >= 3:
                    if sum(x[2] == 1 for x in param['state_total'][-10:]) >= 5:
                        pause_flag = 1
                        wrong_list.append(230)
                    if param['level'] >= 4:
                        if sum(x[3] == 1 for x in param['state_total'][-10:]) >= 5:
                            pause_flag = 1
                            wrong_list.append(240)
                        if param['level'] == 5:
                            if sum(x[4] == 1 for x in param['state_total'][-10:]) >= 5:
                                pause_flag = 1
                                wrong_list.append(250)
                # 
                if param['time_start'] == -1 or param['i'] - param['time_start'] < 2*20:
                    wrong_list = []
                    pause_flag = 0

                if pause_flag == 1:
                    if param['time_end'] == -1:  # 345级
                        param['time_end'] = param['i']
                        param['time_current'] = param['time_end'] - param['time_start']

                    # param['total_list'].append((round(param['time_current'] / param['fps'], 1),
                    #                             param['time_start'], param['time_end'], wrong_list))
                    
                    # 
                    param['wrong_dict'] = self.update_wrong_dict(param, round(param['time_start'] / param['fps'], 1),
                                                                 round(param['time_end'] / param['fps'], 1), wrong_list)
                # else:
                #     if param['time_start'] != -1 and param['time_end'] == -1:
                #         param['time_current'] = param['i'] - param['time_start']
                #         if param['i'] % 20 == 0:
                #             param['wrong_dict'] = self.update_wrong_dict(param, round(param['time_start'] / param['fps'], 1),
                #                                                         round(param['time_end'] / param['fps'], 1), [])

                # 防止计时结束后不退出
                # if param['time_end'] != -1 and param['i'] - param['time_end'] > 3*20:
                #     param['ended'] = param['i']

            if param['began'] == 1 and param['ended'] == 1:
                # 一般不会出现这种情况
                # if param['time_start'] != -1:
                #     param['time_end'] = param['i']
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
                # self.__nCurrentFrameNum = self.__nCurrentFrameNum + 1
                # if not ret:
                #     print("读取视频完毕（{}帧）".format(self.param_dict['i']))
                #     break
                # srcFrame = copy.deepcopy(frame)
                self.param_dict['wrong_dict'] = dict()
                self.param_dict, frame = self.process_one_frame(self.param_dict, kp, frame)
                frame = self.put_text(self.param_dict, frame)
                # self.param_dict['video'].append(frame)
                end = time.time()
                # print(self.param_dict['i'], end - start)
                logger.debug(self.param_dict['i'])
                self.param_dict['i'] += 1
                if len(self.param_dict['wrong_dict']) != 0:
                    return json.dumps(self.param_dict['wrong_dict'])
                elif self.param_dict['i'] % (3*20) == 0:  # 每3s发空串，保持ws连接
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
    cOverHang = CNvOverHang(file_name, difficulty_level, frameNum, outputFile, deviceId)
    cOverHang.init()

    sss = time.time()
    cOverHang.start()
    while not cOverHang.isTailed():
        cparam = cOverHang.processAction()
        # print(cparam)
    logger.info(cOverHang.param_dict['time_current'])
    # encode.encode_frames(cOverHang.param_dict['video'], file_name, 20)
    # draw_kp_2d(cOverHang.param_dict['k_origin'], cOverHang.param_dict['k_processed'], file_name)
    # draw_state(cOverHang.param_dict['state_total'], [6], file_name)
    # for i in range(len(cOverHang.param_dict['state_total'])):
    #     print(cOverHang.param_dict['state_total'][i][6])
    ttt = time.time()
    cOverHang.releaseSelf()
    print(ttt - sss)
