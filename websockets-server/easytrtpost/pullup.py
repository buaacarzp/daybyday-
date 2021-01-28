#!/usr/bin/env python3
import sys
import time
from loguru import logger
import copy
import cv2
from pullup_begin_end_detection import *
from pullup_head_detection import *
from pullup_leg_detection import *
from pullup_arm_detection import *
from pullup_body_detection import *
from draw_utils import *
from basetype import BaseType
import encode
import logging
logging.basicConfig(format="%(asctime)s,%(levelname)s,%(asctime)s,%(filename)s:%(lineno)s:%(message)s",
                    level=logging.DEBUG)
                    #ilename="logserver.log",filemode ="w",level=logging.DEBUG)


class CNvPullup(BaseType):

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
            up_start=-1,
            up_end=-1,
            down_start=-1,
            down_end=-1,
            total_list=[],  # 记录全部动作
            wrong_dict=dict(),
            half_motion=1,  # 0/1，过杠为half_motion，下落后为完整动作

            # updown=0,  # 记录相对运动，以点1作为参考
            updown_delta=0,  # 与前一帧点8的坐标变化

            KEYPOINTS=[],  # 记录腿伸直时的关键点作为基准
            k_origin=[],
            k_processed=[],

            arm_length_list=[],  # 记录最近100帧的手臂长度
            arm_length=0,  # 前臂长度
            scale=0,
            leg_length_list=[],
            leg_length=0,

            arm_straight=0,
            head_pass=0,
            leg_bend=0,
            body_move=0,
            leg_swing=0,

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
        """统计动作总数，记录错误动作原因。

        param['state_total']:(arm_straight, head_pass, leg_bend, body_move, leg_swing,
                                updown_delta, begin_flag, end_flag)
        :return:
        """
        # wrong_list = []
        # print(param['state_total'][-10:])
        # print(i, param['up_start'], param['down_end'], sum(x[5] < -2 for x in param['state_total'][-10:]), sum(x[5] > 2 for x in param['state_total'][-10:]))
        if sum(x[5] < -3 for x in param['state_total'][-10:]) >= 7 \
                or sum(x[5] for x in param['state_total'][-10:]) <= -15:  # 隔帧变化超过2像素或者累计10像素视为运动。最近10帧超过7帧。向上时updown_delta为负。
            if param['up_start'] == -1:
                param['up_start'] = param['i'] - 6  # 最小化动作总帧数，排除前一动作的结束部分
            elif param['up_start'] != -1 and param['down_end'] != -1:  # 检测到新的上升时才会统计上一个动作
                wrong_list = []
                wrong_list = self.is_motion_right(param, wrong_list)

                param['count_including_wrong'] += 1
                if len(wrong_list) == 0:
                    param['count'] += 1
                
                param['wrong_dict'] = self.update_wrong_dict(param, round(param['up_start'] / param['fps'], 2),
                                                             round(param['down_end'] / param['fps'], 2), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))

                param['up_start'] = -1
                param['down_end'] = -1

        if sum(x[5] > 3 for x in param['state_total'][-10:]) >= 7 \
                or sum(x[5] for x in param['state_total'][-10:]) >= 15:
            if param['up_start'] != -1:
                param['down_end'] = param['i'] - 3
                wrong_list = []
                wrong_list = self.is_motion_right(param, wrong_list)
                logger.debug("{} {}", param['i'], wrong_list)
                if len(wrong_list) == 0:
                    param['count'] += 1
                    param['count_including_wrong'] += 1

                    param['wrong_dict'] = self.update_wrong_dict(param, round(param['up_start'] / param['fps'], 1),
                                                                 round(param['down_end'] / param['fps'], 1), wrong_list)

                    logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))
                    param['total_list'].append((param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))

                    param['up_start'] = -1
                    param['down_end'] = -1

        return param['up_start'], param['down_end'], param['count_including_wrong'], param['count'], param['wrong_dict']

    def is_motion_right(self, param, wrong_list):
        """
        param['state_total']:(arm_straight, head_pass, leg_bend, body_move, leg_swing,
                                updown_delta, begin_flag, end_flag)
        """
        # 开始考核后无人状态不存state_total，这里索引需要减去偏移index_offset
        up_start_index = param['up_start'] - param['index_offset']
        down_end_index = param['down_end'] - param['index_offset']
        if param['level'] >= 1:
            # for x in param['state_total'][up_start_index:down_end_index + 10]:
            #     print(x[1])
            # for x in param['state_total'][up_start_index - 9:down_end_index + 1]:
            #     print(x[1])

            # print(sum(x[1] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]),
            #       sum(x[0] == 1 for x in param['state_total'][up_start_index:up_start_index + 10]),
            #       sum(x[0] == 1 for x in param['state_total'][down_end_index - 9:down_end_index + 1]),
            #       sum(x[2] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]),
            #       sum(x[3] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]),
            #       sum(x[4] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]))
            one_list = param['state_total'][up_start_index:down_end_index + 1]
            down_start=0
            for i in range(len(one_list)):
                if sum(x[5] > 3 for x in one_list[:i]) >= 3:
                    down_start = up_start_index + i - 3
                i += 1
            # print("up_start, down_start, down_end = {}, {}, {}".format(up_start_index, down_start, down_end_index))
            up_list = param['state_total'][up_start_index:down_start]
            # if sum(x[1] == 1 and x[5] <= -1 for x in up_list) == 0:
            if sum(x[1] == 1 for x in up_list) == 0:
                wrong_list.append(110)
            if param['level'] >= 2:
                if sum(x[0] == 1 for x in param['state_total'][up_start_index:up_start_index + 10]) == 0 \
                        or sum(x[0] == 1 for x in param['state_total'][down_end_index - 9:down_end_index + 1]) == 0:
                    wrong_list.append(120)
                if param['level'] >= 3:
                    if sum(x[2] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]) > 5:  # 5帧
                        wrong_list.append(130)
                    if param['level'] >= 4:
                        if sum(x[3] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]) > 5:  # 5帧
                            wrong_list.append(140)
                        if param['level'] == 5:
                            if sum(x[4] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]) > 5:  # 5帧
                                wrong_list.append(150)
        return wrong_list
    
    def half_motion_judgement(self, param):
        """统计动作总数，记录错误动作原因。

        param['state_total']:(arm_straight, head_pass, leg_bend, body_move, leg_swing,
                                updown_delta, begin_flag, end_flag)
        :return:
        """
        # wrong_list = []
        # print(param['state_total'][-10:])
        # print(i, param['up_start'], param['up_end'], sum(x[5] < -2 for x in param['state_total'][-10:]), sum(x[5] > 2 for x in param['state_total'][-10:]))
        if sum(x[5] < -3 for x in param['state_total'][-10:]) >= 7 \
                or sum(x[5] for x in param['state_total'][-10:]) <= -15:  # 隔帧变化超过2像素或者累计10像素视为运动。最近10帧超过7帧。向上时updown_delta为负。
            if param['up_start'] == -1:
                param['up_start'] = param['i'] - 6  # 最小化动作总帧数，排除前一动作的结束部分

        if sum(x[5] > 3 for x in param['state_total'][-10:]) >= 7 \
                or sum(x[5] for x in param['state_total'][-10:]) >= 15:
            if param['up_start'] != -1 and param['down_start'] == -1:
                param['up_end'] = param['i'] - 3

                wrong_list = []
                wrong_list = self.is_half_motion_right(param, wrong_list)

                param['count_including_wrong'] += 1
                if len(wrong_list) == 0:
                    param['count'] += 1
                
                param['wrong_dict'] = self.update_wrong_dict(param, round(param['up_start'] / param['fps'], 1),
                                                             round(param['up_end'] / param['fps'], 1), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['up_start'], param['up_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['up_start'], param['up_end'], wrong_list))

                param['up_start'] = -1
                param['up_end'] = -1
                param['down_start'] = -1

        return param['up_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict']

    def is_half_motion_right(self, param, wrong_list):
        """
        param['state_total']:(arm_straight, head_pass, leg_bend, body_move, leg_swing,
                                updown_delta, begin_flag, end_flag)
        """
        # 开始考核后无人状态不存state_total，这里索引需要减去偏移index_offset
        up_start_index = param['up_start'] - param['index_offset']
        up_end_index = param['up_end'] - param['index_offset']
        if param['level'] >= 1:
            # for x in param['state_total'][up_start_index:up_end_index + 10]:
            #     print(x[1])
            # for x in param['state_total'][up_start_index - 9:up_end_index + 1]:
            #     print(x[1])

            # print(sum(x[1] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]),
            #       sum(x[0] == 1 for x in param['state_total'][up_start_index:up_start_index + 10]),
            #       sum(x[0] == 1 for x in param['state_total'][up_end_index - 9:up_end_index + 1]),
            #       sum(x[2] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]),
            #       sum(x[3] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]),
            #       sum(x[4] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]))
            if sum(x[1] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) == 0:
                wrong_list.append(110)
            if param['level'] >= 2:
                if sum(x[0] == 1 for x in param['state_total'][up_start_index:up_start_index + 10]) == 0:
                    wrong_list.append(120)
                if param['level'] >= 3:
                    if sum(x[2] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) > 5:  # 5帧
                        wrong_list.append(130)
                    if param['level'] >= 4:
                        if sum(x[3] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) > 5:  # 5帧
                            wrong_list.append(140)
                        if param['level'] == 5:
                            if sum(x[4] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) > 5:  # 5帧
                                wrong_list.append(150)
        return wrong_list
    
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
        # 从最近100帧中获取最大腿长
        if get_leg_length(keypoints) != -1:
            param['leg_length'] = get_leg_length(keypoints)
        param['leg_length_list'].append(param['leg_length'])
        if len(param['leg_length_list']) > 50:
            param['leg_length_list'].pop(0)
        if param['leg_length'] == max(param['leg_length_list']):
            param['KEYPOINTS'] = copy.deepcopy(keypoints)

        # 获取比例尺
        if get_arm_length(keypoints) != -1:
            param['arm_length'] = get_arm_length(keypoints)
        param['arm_length_list'].append(param['arm_length'])
        if len(param['arm_length_list']) > 50:
            param['arm_length_list'].pop(0)
        if param['arm_length'] == max(param['arm_length_list']):
            # print(arm_length)
            param['scale'] = get_length_scale(keypoints[3], keypoints[4], 25)  # 前臂参考长度

        # 获取各状态，否则沿用上一帧的状态
        if is_arm_straight(keypoints) != -1:
            param['arm_straight'] = is_arm_straight(keypoints)
        if is_head_pass(keypoints) != -1:
            param['head_pass'] = is_head_pass(keypoints)
        if is_leg_bend(keypoints) != -1:
            param['leg_bend'] = is_leg_bend(keypoints)
        if is_body_move(keypoints, param['scale']) != -1:
            param['body_move'] = is_body_move(keypoints, param['scale'])
        if is_leg_swing(keypoints, param['KEYPOINTS']) != -1 and is_leg_open(keypoints) != -1:
            param['leg_swing'] = is_leg_swing(keypoints, param['KEYPOINTS']) or is_leg_open(keypoints)

        if is_begin(keypoints) != -1:
            param['begin_flag'] = is_begin(keypoints)  # 上杠
        if is_end(keypoints) != -1:
            param['end_flag'] = is_end(keypoints)  # 下杠

        if len(param['state_total']) > 1:
            param['updown_delta'] = round(param['k_origin'][-1][8][1] - param['k_origin'][-2][8][1])

        param['state_total'].append((param['arm_straight'], param['head_pass'], param['leg_bend'], param['body_move'],
                                     param['leg_swing'], param['updown_delta'], param['begin_flag'], param['end_flag']))

        # 判定手臂举起，只会进入一次
        if len(param['state_total']) >= 5:
            if sum(x[6] == 1 for x in param['state_total'][-5:]) >= 3 and param['began'] == -1:  # param['begin_flag'] == 1
                param['began'] = 1
                param['begin_time'] = param['i'] - 3
                logger.info("检测到准备动作")

        if len(param['state_total']) >= 20:
            if param['began'] == 1 and param['ended'] == -1:
                # 上、下视为完整动作时
                if param['half_motion'] == 0:
                    param['up_start'], param['down_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)
                else:
                    param['up_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.half_motion_judgement(param)
            
            # print(sum(x[7] == 1 for x in param['state_total'][-10:]),
            #       param['ended'] == -1, param['began'] == 1,
            #       param['i'] - param['begin_time'] >= 3*20)
            
            # 判定手臂放下，只会进入一次
            if sum(x[7] == 1 for x in param['state_total'][-10:]) >= 7 and param['ended'] == -1 \
                    and param['began'] == 1 and param['i'] - param['begin_time'] >= 2*20:  # 开始后的前2秒不计结束
                param['ended'] = 1
                param['end_time'] = param['i'] - 7
                logger.info("检测到违停动作")
            
            # 上、下视为完整动作时
            if param['half_motion'] == 0:
                if param['began'] == 1 and param['ended'] == 1:
                    # print(param['down_end'], param['up_start'])
                    # if param['down_end'] - param['up_start'] > 10:
                    #     param['up_start'], param['down_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)

                    if param['up_start'] != -1:
                        if param['down_end'] == -1:  # 有头无尾，很少出现这种情形
                            param['down_end'] = param['end_time']
                        
                        wrong_list = []
                        wrong_list = self.is_motion_right(param, wrong_list)

                        param['count_including_wrong'] += 1
                        if len(wrong_list) == 0:
                            param['count'] += 1
                        # print(wrong_list)
                        param['wrong_dict'] = self.update_wrong_dict(param, round(param['up_start'] / param['fps'], 1),
                                                                     round(param['down_end'] / param['fps'], 1), wrong_list)

                        logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))
                        param['total_list'].append((param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))

                        param['up_start'] = -1
                        param['down_end'] = -1

                    # if param['down_end'] == -1:
                    #     param['wrong_dict'] = self.update_wrong_dict(param, round(param['i'] / param['fps'], 1),
                    #                                                 round(param['i'] / param['fps'], 1), [-3])  # 输出停止信息

            # if param['count'] != 0:  # 防止处于杠下状态时输出一堆0
            #     param['total_count'].append(param['count'])
            #     param['count'] = 0
            # param['arm_straight'] = 0  # 结束时各状态清0
            # param['head_pass'] = 0
            # param['leg_bend'] = 0
            # param['body_move'] = 0
            # param['leg_swing'] = 0
        return param, frame

    def put_text(self, param, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'count: {}/{}    Level {}'.format(str(param['count']), str(param['count_including_wrong']),
                                                             str(param['level'])), (0, 15), font, 1.2/2, (255, 255, 0), 2)
        cv2.putText(frame, 'head_pass: ' + str(param['head_pass']), (0, 30), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'arm_straight: ' + str(param['arm_straight']), (0, 45), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'leg_bend: ' + str(param['leg_bend']), (0, 60), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'body_move: ' + str(param['body_move']), (0, 75), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'leg_swing: ' + str(param['leg_swing']), (0, 90), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_flag/end_flag: ' + str(param['begin_flag']) + str(param['end_flag']), (0, 115), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_time/end_time: ' + str(param['begin_time']) + str(param['end_time']), (0, 130), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'i: ' + str(param['i']), (0, 145), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'time: ' + str(round(param['i'] / param['fps'], 1)) + 's', (0, 160), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'updown_delta: ' + str(param['updown_delta']), (0, 175), font, 1.0/2, (0, 0, 255), 2)
        cv2.putText(frame, 'up_start/up_end/down_end: ' + str(param['up_start']) + str(param['up_end']) + str(param['down_end']), (0, 190), font, 1.0/2, (0, 0, 255), 2)
        return frame


# if __name__ == '__main__':
#     file_name = sys.argv[1]
#     difficulty_level = sys.argv[2]
#     frameNum = sys.argv[3]
#     outputFile = sys.argv[4]
#     deviceId = sys.argv[5]
#     iii = time.time()
#     cPullup = CNvPullup(file_name, difficulty_level, frameNum, outputFile, deviceId)
#     cPullup.init()
#     sss = time.time()
#     cPullup.start()
#     while not cPullup.isTailed():
#         cparam = cPullup.processAction()
#         # print(cparam)
#     logger.info("{} {}", cPullup.param_dict['count'], cPullup.param_dict['count_including_wrong'])
#     logger.info("{}", cPullup.param_dict['total_list'])
#     # encode.encode_frames(cPullup.param_dict['video'], file_name, 20)
#     cPullup.releaseSelf()

#     ttt = time.time()
#     print(ttt - sss)

if __name__ == '__main__':
    # file_name = sys.argv[1]
    # difficulty_level = sys.argv[2]
    # frameNum = sys.argv[3]
    # outputFile = sys.argv[4]
    # deviceId = int(sys.argv[5])
    file_name,difficulty_level,frameNum,outputFile,deviceId='0000.mp4', '5', '200', 'dfl.mp4', '0'#'rtsp://admin:123456@192.168.1.102:554/mpeg4cif', '5', '200', 'dfl.mp4', '0'
    iii = time.time()
    cPullup = CNvPullup()
    mmm = time.time()
    cPullup.init()
    cPullup.start(file_name, difficulty_level, frameNum, outputFile, deviceId)
    i = 0
    while not cPullup.isTailed():
        # cPushup.stop()
        cparam = cPullup.processAction()
        logging.debug(f"i={i},cparam={cparam}")
        # cPullup.stop()#实际是控制往队列里面存数据，不是让算法结束
        i+=1
        # break
        
    # encode.encode_frames(cPushup.param_dict['video'], file_name, 20)
    logger.info("{} {}", cPullup.param_dict['count'], cPullup.param_dict['count_including_wrong'])
    logger.info("{}", cPullup.param_dict['total_list'])
    # draw_kp_2d(cPushup.param_dict['k_origin'], cPushup.param_dict['k_processed'], file_name)
    # draw_state(cPushup.param_dict['state_total'], [0], file_name)
    # for i in range(len(cPushup.param_dict['state_total'])):
    #     print(cPushup.param_dict['state_total'][i][7])
    cPullup.releaseSelf()
    # print("__init__:", round(mmm-iii, 4), "\ninit:", round(sss-mmm, 4), "\nstart:", round(xxx-sss, 4), "\nwhile:", round(yyy-xxx, 4), round(ttt-sss, 4))
