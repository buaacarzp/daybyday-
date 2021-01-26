#!/usr/bin/env python3
import sys
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


class CNvPushup(BaseType):
    # def __init__(self, rtsp_address="", level="", total_frame_num="", outputfile=""):
    #     super().__init__(rtsp_address, level, total_frame_num, outputfile)

    def init_param(self):
        param = dict(
            fps=self.prod.fps,
            width=self.prod.rtsp_width,
            height=self.prod.rtsp_height,

            # print("考核等级：" + level)  # 1~5
            level=self.level,

            count=0,
            count_including_wrong=0,

            video=[],  # 保存标注后的视频
            state_total=[],  # 记录全部状态
            down_start=-1,
            up_end=-1,
            up_start=-1,
            total_list=[],  # 记录全部动作
            wrong_dict=dict(),

            # updown=0,  # 记录相对运动，以点1作为参考
            updown_delta=0,  # 与前一帧点1的坐标变化

            KEYPOINTS=[],  # 记录手臂伸直时的关键点作为基准
            k_origin=[],
            k_processed=[],

            arm_straight=0,
            arm_length_list=[],  # 记录最近100帧的手臂长度
            arm_length=0,
            mean_arm_length=110,  # 手臂总长默认110，防止除0报错
            ground=0,
            mean_ground=240,  # 地面默认坐标240
            ground_list=[],
            knee_on_ground=0,
            body2ground=0,
            shoulder_below_elbow=0,
            scale=0,
            waist_bend=0,
            butt_bend=0,
            foot_open=0,

            begin_flag=-1,
            end_flag=-1,
            began=-1,
            ended=-1,
            begin_time=-1,
            end_time=-1,
            time_count_down=20,

            i=0,
            index_offset=-1,
            processed_num=np.ones((19,))*5
        )
        return param

    def motion_judgement(self, param):
        """统计动作总数，记录错误动作原因

        :param param: state_total: (ground, arm_straight, waist_bend, butt_bend,
                                    knee_on_ground, foot_open, body2ground, updown_delta,
                                    begin_flag, end_flag)
        :return:
        """
        # wrong_list = []
        # print(param['state_total'][-10:])
        # print(param['i'], param['down_start'], param['up_end'], param['updown_delta'],
        #       sum(x[7] > 2 for x in param['state_total'][-5:]) >= 3,
        #       sum(x[7] for x in param['state_total'][-5:]) > 10,
        #       sum(x[7] < -2 for x in param['state_total'][-5:]) >= 3,
        #       sum(x[7] for x in param['state_total'][-5:]) < -10)
        up_start_index = param['up_start'] - param['index_offset']  # state_total索引由于无人状态的偏移。（前端报出有效0/1的问题）
        if sum(x[7] > 2 for x in param['state_total'][-5:]) >= 3 \
                and sum(x[7] for x in param['state_total'][-5:]) > 10:
            if param['down_start'] == -1:
                param['down_start'] = param['i'] - 3
            elif param['down_start'] != -1 and param['up_end'] != -1:  # 下降时的动作判断是为了正确统计因手臂未伸直而未统计的错误动作
                wrong_list = []
                wrong_list = self.is_motion_right(param, wrong_list)
                param['count_including_wrong'] += 1
                # if len(wrong_list) == 0:  # 下降时只可能统计错误动作
                #     param['count'] += 1

                param['wrong_dict'] = self.update_wrong_dict(param, round(param['down_start'] / param['fps'], 1),
                                                             round(param['up_end'] / param['fps'], 1), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))

                param['down_start'] = -1
                param['up_end'] = -1
                param['up_start'] = -1

        if sum(x[7] < -2 for x in param['state_total'][-5:]) >= 3 \
                and sum(x[7] for x in param['state_total'][-5:]) < -10:
            if param['down_start'] != -1:
                if param['up_start'] == -1:
                    param['up_start'] = param['i']
                param['up_end'] = param['i']  # 修改为撑起时判断动作正误后，需要统计到当前帧
        # 随时检测是否满足正确动作；错误动作的统计只在第二个动作周期到来时完成
        if param['down_start'] != -1 and param['up_end'] != -1:
            param['up_end'] = param['i']
            wrong_list = []
            wrong_list = self.is_motion_right(param, wrong_list)
            logger.debug("{} {}", param['i'], wrong_list)
            if 313 not in wrong_list and sum(x[1] == 1 for x in param['state_total'][up_start_index:]) >= 3:  # 需要满足有3帧手臂伸直
                if len(wrong_list) == 0:
                    param['count'] += 1
                param['count_including_wrong'] += 1
                param['wrong_dict'] = self.update_wrong_dict(param, round(param['down_start'] / param['fps'], 1),
                                                             round(param['up_end'] / param['fps'], 1), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))

                param['down_start'] = -1
                param['up_end'] = -1
                param['up_start'] = -1

        return param['down_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict']

    def is_motion_right(self, param, wrong_list):
        """
        state_total: (ground, arm_straight, waist_bend, butt_bend,
                            knee_on_ground, foot_open, body2ground, updown_delta,
                            begin_flag, end_flag)
        """
        # 开始考核后无人状态不存state_total，这里索引需要减去偏移index_offset
        down_start_index = param['down_start'] - param['index_offset']
        up_end_index = param['up_end'] - param['index_offset']
        up_start_index = param['up_start'] - param['index_offset']

        if param['level'] >= 1:
            # for x in param['state_total'][down_start_index:up_end_index + 10]:
            #     print(x[1])
            # for x in param['state_total'][up_end_index - 9:up_end_index + 1]:
            #     print(x[1])
            # print(sum(x[1] == 1 for x in param['state_total'][down_start_index:down_start_index + 10]),
            #     sum(x[1] == 1 for x in param['state_total'][up_end_index - 9:up_end_index + 1]),
            #     sum(x[2] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]),
            #     sum(x[3] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]),
            #     sum(x[4] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]),
            #     sum(x[5] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]),
            #     min([x[6] for x in param['state_total'][down_start_index:up_end_index + 1]], default=999))
            if sum(x[4] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) > 5:  # 5帧
                wrong_list.append(311)
            if min([x[6] for x in param['state_total'][down_start_index:up_end_index + 1]], default=35) > 35:  # 身体离地
                if sum(x[10] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) == 0:  # 肩关节低于肘关节时视为正确动作
                    wrong_list.append(312)
            # if sum(x[1] == 1 for x in param['state_total'][down_start_index:down_start_index + 10]) == 0 \
            #         or sum(x[1] == 1 for x in param['state_total'][up_end_index - 9:up_end_index + 1]) == 0:
            if sum(x[1] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) == 0:
                # print(sum(x[1] == 1 for x in param['state_total'][down_start_index:down_start_index + 10]))
                # print(sum(x[1] == 1 for x in param['state_total'][up_end_index - 9:up_end_index + 1]))
                wrong_list.append(313)
            if param['level'] >= 2:
                if sum(x[2] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) > 5:  # 5帧
                    wrong_list.append(320)
                if param['level'] >= 3:
                    if sum(x[3] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) > 5:  # 5帧
                        wrong_list.append(330)
                    if param['level'] >= 4:
                        if sum(x[5] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) > 5:  # 5帧
                            wrong_list.append(340)
                        if param['level'] == 5:
                            # 这里要找过程中距地最小的点
                            if min([x[6] for x in param['state_total'][down_start_index:up_end_index + 1]], default=30) > 25:  # 身体离地
                                if sum(x[10] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) == 0:
                                    wrong_list.append(350)

        return wrong_list

    def update_wrong_dict(self, param, down_start, up_end, wrong_list):
        # if not os.path.exists('logs'):
        #     os.mkdir('logs')
        # if not os.path.exists('logs/wrong_list.json'):
        #     os.mknod('logs/wrong_list.json')
        #
        status = [0] if len(wrong_list) == 0 else wrong_list
        time_period = (down_start, up_end)
        param['wrong_dict'] = {'status': status, 'total': param['count_including_wrong'], 'count': param['count'], 'time': time_period, 'msg': ""}
        # with open('logs/wrong_list.json', 'a+') as f:
        #     json.dump(param['wrong_dict'], f)
        #     f.write('\n')

        return param['wrong_dict']

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

        keypoints = keypoints[0]
        param['k_origin'].append(copy.deepcopy(keypoints))
        keypoints, param['processed_num'] = data_process(keypoints, param['k_origin'], param['k_processed'], param['height'], param['processed_num'])  # 可变对象是引用传递
        # # 8点在使用前需要用处理过的9/12点重新赋值，减小丢失的影响
        # keypoints[8] = copy.deepcopy([round((keypoints[9][0] + keypoints[12][0])/2), round((keypoints[9][1] + keypoints[12][1])/2), (keypoints[9][2] + keypoints[12][2])/2])
        param['k_processed'].append(keypoints)
        # param['keypoints'] = copy.deepcopy(keypoints)

        frame = draw_parts(keypoints, frame)  # 绘制渲染处理后的骨骼

        if is_begin(keypoints) != -1:
            param['begin_flag'] = is_begin(keypoints)
        if is_end(keypoints) != -1:
            param['end_flag'] = is_end(keypoints)

        # 获取比例尺
        avalue = get_arm_total_length(keypoints)
        if avalue != -1:
            param['arm_length'] = avalue
        # print(param['arm_length'])
        if 50 < param['arm_length'] < 200:
            param['arm_length_list'].append(param['arm_length'])
            param['arm_length_list'], param['mean_arm_length'] = get_mean_value(param['arm_length_list'], param['i'])
        # if param['arm_length'] == max(param['arm_length_list']):
        #     param['KEYPOINTS'] = copy.deepcopy(keypoints)
        #     param['scale'] = get_length_scale(keypoints[3], keypoints[4], 30)
        param['scale'] = 60/np.array(param['mean_arm_length'])  # 前臂+上臂=60

        ground_value = get_ground_coordinate(keypoints, param['scale'])
        if ground_value != -1:
            param['ground'] = ground_value
        # print(ground_value, param['ground'])
        if 180 < param['ground'] < 270:
            param['ground_list'].append(param['ground'])
            param['ground_list'], param['mean_ground'] = get_mean_value(param['ground_list'], param['i'])

        p2gvalue = get_point2ground_distance(keypoints[1], param['mean_ground'])
        if p2gvalue != -1.:
            param['body2ground'] = p2gvalue * param['scale']

        sbevalue = is_shoulder_below_elbow(keypoints)
        if sbevalue != -1:
            param['shoulder_below_elbow'] = sbevalue

        kgvalue = is_knee_on_ground(keypoints, param['mean_ground'], param['scale'])
        param['knee_on_ground'] = 0 if kgvalue != 1 else 1  # 不沿用上一帧的状态
        if is_arm_straight(keypoints) != -1 and is_shoulder_up(keypoints, param['mean_arm_length']) != -1:  # 辅助判断手臂伸直
            param['arm_straight'] = is_arm_straight(keypoints) and is_shoulder_up(keypoints, param['mean_arm_length'])
        # print(param['arm_straight'])

        if is_foot_open(keypoints, param['scale']) != -1:
            param['foot_open'] = is_foot_open(keypoints, param['scale'])

        if is_waist_bend(keypoints) != -1:
            param['waist_bend'] = is_waist_bend(keypoints)
        bbvalue = is_butt_bend(keypoints)
        param['butt_bend'] = 0 if bbvalue != 1 else 1  # 不沿用上一帧的状态

        if len(param['state_total']) > 0:
            param['updown_delta'] = param['k_processed'][-1][2][1] - param['k_processed'][-2][2][1]
            # print(updown_delta)
        param['state_total'].append((param['mean_ground'], param['arm_straight'], param['waist_bend'], param['butt_bend'],
                                     param['knee_on_ground'], param['foot_open'], param['body2ground'],
                                     param['updown_delta'], param['begin_flag'], param['end_flag'],
                                     param['shoulder_below_elbow']))

        # 判定人趴下，只会进入一次
        if len(param['state_total']) >= 5:
            if sum(x[8] == 1 for x in param['state_total'][-5:]) >= 3 and param['began'] == -1:  # param['begin_flag'] == 1
                param['began'] = 1
                param['begin_time'] = param['i'] - 3
                logger.info("检测到准备动作")

        if len(param['state_total']) >= 20:
            if param['began'] == 1 and param['ended'] == -1:
                param['down_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)
            
            # 判定人站起，只会进入一次
            if sum(x[9] == 1 for x in param['state_total'][-5:]) >= 3 and param['ended'] == -1 \
                    and param['began'] == 1 and param['i'] - param['begin_time'] >= 2*20:  # 开始后的前2秒不计结束
                param['ended'] = 1
                param['end_time'] = param['i'] - 3
                logger.info("检测到违停动作")
            
            if param['began'] == 1 and param['ended'] == 1:
                # print(param['up_end'], param['down_start'])
                # if param['up_end'] - param['down_start'] > 10:
                #     param['down_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)
                if param['down_start'] != -1 and param['up_end'] != -1:  # 下降、上升均检测到时，才判断最后一个动作
                    wrong_list = []
                    wrong_list = self.is_motion_right(param, wrong_list)

                    param['count_including_wrong'] += 1
                    if len(wrong_list) == 0:
                        param['count'] += 1
                    param['wrong_dict'] = self.update_wrong_dict(param, round(param['down_start'] / param['fps'], 1),
                                                                 round(param['up_end'] / param['fps'], 1), wrong_list)

                    logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))
                    param['total_list'].append((param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))

                    param['down_start'] = -1
                    param['up_end'] = -1

                # if param['up_end'] == -1:
                #     param['wrong_dict'] = self.update_wrong_dict(param, round(param['i'] / param['fps'], 1),
                #                                                    round(param['i'] / param['fps'], 1), [-3])  # 输出停止信息
            # if count != 0:  # 防止处于非准备状态时输出一堆0
            #     total_count.append(count)
            #     count = 0

            # param['arm_straight'] = 0
            # param['waist_bend'] = 0
            # param['butt_bend'] = 0
            # param['knee_on_ground'] = 0
            # param['foot_open'] = 0
            # param['body2ground'] = 0
        return param, frame

    def put_text(self, param, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'count: {}/{}    Level {}'.format(str(param['count']), str(param['count_including_wrong']),
                                                             str(param['level'])), (0, 15), font, 1.2/2, (255, 255, 0), 2)
        cv2.putText(frame, 'arm_straight: ' + str(param['arm_straight']), (0, 40), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'waist_bend: ' + str(param['waist_bend']), (0, 55), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'butt_bend: ' + str(param['butt_bend']), (0, 70), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'knee_on_ground: ' + str(param['knee_on_ground']), (0, 85), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'foot_open: ' + str(param['foot_open']), (0, 100), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'body2ground: ' + str(round(param['body2ground'])), (0, 115), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_flag/end_flag: ' + str(param['begin_flag']) + str(param['end_flag']), (0, 130), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_time/end_time: ' + str(param['begin_time']) + str(param['end_time']), (0, 145), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'i: ' + str(param['i']), (0, 160), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'time: ' + str(round(param['i'] / param['fps'], 1)) + 's', (0, 175), font, 1.0/2, (0, 0, 255), 2)

        cv2.putText(frame, 'down_start/up_start/up_end: ' + str(param['down_start']) + str(param['up_start']) + str(param['up_end']), (0, 200), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'updown_delta: ' + str(param['updown_delta']), (0, 215), font, 1.0/2, (0, 0, 255), 2)

        return frame


if __name__ == '__main__':
    file_name = sys.argv[1]
    difficulty_level = sys.argv[2]
    frameNum = sys.argv[3]
    outputFile = sys.argv[4]
    deviceId = int(sys.argv[5])
    # file_name = "rtsp://admin:admin12345@192.168.1.124/cam/realmonitor?channel=1&subtype=0"
    # difficulty_level= "5"
    # frameNum = "2400"
    # outputFile = "test.mp4"
    iii = time.time()
    cPushup = CNvPushup(file_name, difficulty_level, frameNum, outputFile, deviceId)
    mmm = time.time()
    cPushup.init()
    # time.sleep(5)
    sss = time.time()

    cPushup.start()
    xxx = time.time()
    while not cPushup.isTailed():
        cparam = cPushup.processAction()
        # print(cparam)
    # for i in range(3):
    #     time.sleep(1)
    #     print(3-i)
    # print("开始释放")
    yyy = time.time()
    # encode.encode_frames(cPushup.param_dict['video'], file_name, 20)
    logger.info("{} {}", cPushup.param_dict['count'], cPushup.param_dict['count_including_wrong'])
    logger.info("{}", cPushup.param_dict['total_list'])
    # draw_kp_2d(cPushup.param_dict['k_origin'], cPushup.param_dict['k_processed'], file_name)
    # draw_state(cPushup.param_dict['state_total'], [0], file_name)
    # for i in range(len(cPushup.param_dict['state_total'])):
    #     print(cPushup.param_dict['state_total'][i][7])
    cPushup.releaseSelf()
    # print("运行释放完毕")
    # time.sleep(5)
    ttt = time.time()
    print("__init__:", round(mmm-iii, 4), "\ninit:", round(sss-mmm, 4), "\nstart:", round(xxx-sss, 4), "\nwhile:", round(yyy-xxx, 4), round(ttt-sss, 4))
