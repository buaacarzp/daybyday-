#!/usr/bin/env python3
import sys
import time
from loguru import logger
import copy
import cv2
from situp_begin_end_detection import *
from situp_arm_detection import *
from situp_body_detection import *
from situp_leg_detection import *
from pushup_body_detection import get_point2ground_distance
from draw_utils import *
from basetype import BaseType
import encode
import logging
logging.basicConfig(format="%(asctime)s,%(levelname)s,%(asctime)s,%(filename)s:%(lineno)s:%(message)s",
                    level=logging.DEBUG)
                    #ilename="logserver.log",filemode ="w",level=logging.DEBUG)

class CNvSitup(BaseType):

    def init_param(self):
        param = dict(
            fps=self.prod.fps,
            width=self.prod.rtsp_width,
            height=self.prod.rtsp_height,

            # print("考核等级：" + level)  # 1~5
            level=self.level,

            total_count=[],
            count=0,
            count_including_wrong=0,

            video=[],  # 保存标注后的视频
            state_total=[],  # 记录全部状态
            up_start=-1,
            down_end=-1,
            sit_motion=1,  # 准备姿势是否坐立
            down_start=-1,  # 准备姿势为坐立时
            up_end=-1,
            sit_up_start=-1,
            total_list=[],  # 记录全部动作
            wrong_dict=dict(),

            updown_delta=0,  # 与前一帧点1的坐标变化

            KEYPOINTS=[],  # 记录腿伸直时的关键点作为基准
            k_origin=[],
            k_processed=[],

            ground=0,
            ground_list=[],
            back_horizontal=0,
            angle_back_horizontal=0,
            angle_delta=0,
            shoulder2ground=0,
            arm_length_list=[],
            arm_length=0,
            arm_length_list_r=[],
            arm_length_r=0,
            leg_length=0,
            leg_length_list=[],
            scale=0,
            arm_open=0,
            elbow_touch=0,
            elbow_pass=0,

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

            param['state_total']:(ground, back_horizontal, arm_open, elbow_touch, elbow_pass,
                                  shoulder2ground, updown_delta, begin_flag, end_flag)
            :return:
            """
        # wrong_list = []
        # print(param['state_total'][-10:])
        # print(i, param['up_start'], param['down_end'], param['count_including_wrong'])
        # 对于仰卧起坐，用updown_delta去寻找动作的起止点有误差：5点超过最高点后下降会导致误判；应该换用81与水平的夹角。
        if sum(x[6] < -3 for x in param['state_total'][-10:]) >= 7 \
                or sum(x[6] for x in param['state_total'][-10:]) <= -15:
            if param['up_start'] == -1:
                param['up_start'] = param['i'] - 6
            elif param['up_start'] != -1 and param['down_end'] != -1:
                wrong_list = []
                wrong_list = self.is_motion_right(param, wrong_list)
                param['count_including_wrong'] += 1
                if len(wrong_list) == 0:
                    param['count'] += 1

                param['wrong_dict'] = self.update_wrong_dict(param, round(param['up_start'] / param['fps'], 1),
                                                             round(param['down_end'] / param['fps'], 1), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['up_start'], param['down_end'], wrong_list))

                param['up_start'] = -1
                param['down_end'] = -1

        if (sum(x[6] > 3 for x in param['state_total'][-10:]) >= 7 or sum(x[6] for x in param['state_total'][-10:]) >= 15) \
                and param['state_total'][-1][5] < 20:  # 5点超过最高点后下降会导致误判
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
        # 开始考核后无人状态不存state_total，这里索引需要减去偏移index_offset
        up_start_index = param['up_start'] - param['index_offset']
        down_end_index = param['down_end'] - param['index_offset']
        if param['level'] >= 1:
            # for x in param['state_total'][up_start_index:down_end_index + 10]:
            #     print(x[1])
            # for x in param['state_total'][up_start_index - 9:down_end_index + 1]:
            #     print(x[1])

            # print(sum(x[1] == 1 for x in param['state_total'][up_start_index:up_start_index + 10]),
            #       sum(x[1] == 1 for x in param['state_total'][down_end_index - 9:down_end_index + 1]),
            #       sum(x[2] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]),
            #       min([x[5] for x in param['state_total'][up_start_index:down_end_index + 1]], default=999),
            #       sum(x[3] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]),
            #       sum(x[4] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]))
            if min([x[5] for x in param['state_total'][up_start_index:down_end_index + 1]], default=25) > 25:  # 双肩距地
                wrong_list.append(411)
            if sum(x[1] == 1 for x in param['state_total'][up_start_index:up_start_index + 10]) == 0 \
                    or sum(x[1] == 1 for x in param['state_total'][down_end_index - 9:down_end_index + 1]) == 0:
                wrong_list.append(412)
            if param['level'] >= 2:
                if sum(x[2] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]) > 5:  # 5帧
                    wrong_list.append(420)
                if param['level'] >= 3:
                    if min([x[5] for x in param['state_total'][up_start_index:down_end_index + 1]], default=15) > 15:  # 双肩距地
                        wrong_list.append(430)
                    if param['level'] >= 4:
                        if sum(x[3] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]) == 0:
                            wrong_list.append(440)
                        if param['level'] == 5:
                            if sum(x[4] == 1 for x in param['state_total'][up_start_index:down_end_index + 1]) == 0:
                                wrong_list.append(450)

        return wrong_list

    def sit_motion_judgement(self, param):
        """统计动作总数，记录错误动作原因

            param['state_total']:(ground, back_horizontal, arm_open, elbow_touch, elbow_pass,
                                  shoulder2ground, updown_delta, begin_flag, end_flag, angle_delta)
            :return:
            """
        # wrong_list = []
        # print(param['state_total'][-10:])
        # print(i, param['down_start'], param['up_end'], param['count_including_wrong'])
        up_start_index = param['sit_up_start'] - param['index_offset']  # state_total索引由于无人状态的偏移。（前端报出有效0/1的问题）
        if sum(x[9] < -2 for x in param['state_total'][-5:]) >= 3 \
                and sum(x[9] for x in param['state_total'][-5:]) < -10:
            if param['down_start'] == -1:
                param['down_start'] = param['i'] - 3
            elif param['down_start'] != -1 and param['up_end'] != -1:
                wrong_list = []
                wrong_list = self.is_sit_motion_right(param, wrong_list)
                param['count_including_wrong'] += 1
                if len(wrong_list) == 0:
                    param['count'] += 1

                param['wrong_dict'] = self.update_wrong_dict(param, round(param['down_start'] / param['fps'], 1),
                                                             round(param['up_end'] / param['fps'], 1), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))

                param['down_start'] = -1
                param['up_end'] = -1
                param['sit_up_start'] = -1

        if sum(x[9] > 2 for x in param['state_total'][-5:]) >= 3 \
                and sum(x[9] for x in param['state_total'][-5:]) > 10:
            if param['down_start'] != -1:
                if param['sit_up_start'] == -1:
                    param['sit_up_start'] = param['i']
                param['up_end'] = param['i']

        # 原来是在上升阶段判断，存在动作区间不完整的问题
        # 单独出来以后，上升至没有明显升降的时间时，也进行动作判断；如果动作合格，不用等待第二个动作的下降即可汇报。
        if param['down_start'] != -1 and param['up_end'] != -1:
            param['up_end'] = param['i']
            wrong_list = []
            wrong_list = self.is_sit_motion_right(param, wrong_list)
            logger.debug("{} {}", param['i'], wrong_list)
            if 450 not in wrong_list and sum(x[4] == 1 for x in param['state_total'][up_start_index:]) >= 3:
                if len(wrong_list) == 0:
                    param['count'] += 1
                param['count_including_wrong'] += 1

                param['wrong_dict'] = self.update_wrong_dict(param, round(param['down_start'] / param['fps'], 1),
                                                             round(param['up_end'] / param['fps'], 1), wrong_list)

                logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))
                param['total_list'].append((param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))

                param['down_start'] = -1
                param['up_end'] = -1
                param['sit_up_start'] = -1

        return param['down_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict']

    def is_sit_motion_right(self, param, wrong_list):
        # 开始考核后无人状态不存state_total，这里索引需要减去偏移index_offset
        down_start_index = param['down_start'] - param['index_offset']
        up_end_index = param['up_end'] - param['index_offset']
        up_start_index = param['sit_up_start'] - param['index_offset']
        if param['level'] >= 1:
            # for x in param['state_total'][down_start_index:up_end_index + 10]:
            #     print(x[1])
            # for x in param['state_total'][down_start_index - 9:up_end_index + 1]:
            #     print(x[1])

            # print(sum(x[1] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]),  # 412
            #       sum(x[2] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]),  # 420
            #       min([x[5] for x in param['state_total'][down_start_index:up_end_index + 1]], default=999),
            #       sum(x[3] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]),
            #       sum(x[4] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]))
            if min([x[5] for x in param['state_total'][down_start_index:up_end_index + 1]], default=25) > 25:  # 落地双肩离地>15厘米
                wrong_list.append(411)
            if sum(x[1] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) < 3:  # 准备姿势为坐立时，需要寻找动作全程中的躺平点
                wrong_list.append(412)
            if param['level'] >= 2:
                frame_num = (up_end_index - down_start_index) / 3  # 双手交叉检测错误动作界定帧数：3、总帧数的1/3、10帧
                if frame_num > 10:
                    frame_num = 10
                elif frame_num < 3:
                    frame_num = 3
                if sum(x[2] == 1 for x in param['state_total'][down_start_index:up_end_index + 1]) > frame_num:  # 一个完整动作中不规范姿态的帧数
                    wrong_list.append(420)
                if param['level'] >= 3:
                    if min([x[5] for x in param['state_total'][down_start_index:up_end_index + 1]], default=15) > 15:  # 双肩触地
                        wrong_list.append(430)
                    if param['level'] >= 4:
                        if sum(x[3] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) < 3:
                            wrong_list.append(440)
                        if param['level'] == 5:
                            if sum(x[4] == 1 for x in param['state_total'][up_start_index:up_end_index + 1]) < 3:
                                wrong_list.append(450)

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

        if is_begin(keypoints) != -1:
            param['begin_flag'] = is_begin(keypoints)
        if is_end(keypoints) != -1:
            param['end_flag'] = is_end(keypoints)

        # 获取比例尺
        llength = get_leg_length(keypoints[13], keypoints[14])
        if llength != -1:
            param['leg_length'] = llength
        param['leg_length_list'].append(param['leg_length'])
        param['leg_length_list'], mean_leg_length = get_mean_length(param['leg_length_list'], param['i'])
        # if param['arm_length'] == max(param['arm_length_list']):
        #     param['scale'] = get_length_scale(keypoints[5], keypoints[6], const.LENGTH_UPPER_ARM)
        param['scale'] = 40/np.array(mean_leg_length)  # 小腿长度视为40cm
        # print(param['scale'])

        param['ground_list'].append(keypoints[14][1])  # 8点备用
        param['ground_list'], param['ground'] = get_mean_value(param['ground_list'], param['i'])

        # 获取各状态
        if is_back_horizontal(keypoints) != -1:
            param['back_horizontal'] = is_back_horizontal(keypoints)
            param['angle_back_horizontal'] = get_angle_back_horizontal(keypoints)
            # print(param['angle_back_horizontal'])
        if get_point2ground_distance(keypoints[5], param['ground']) != -1.:
            param['shoulder2ground'] = get_point2ground_distance(keypoints[5], param['ground']) * param['scale']
        aovalue = is_arm_open(keypoints, param['scale'])
        param['arm_open'] = 0 if aovalue != 1 else 1  # 不沿用上一帧的状态
        if is_elbow_touch_leg(keypoints, param['scale']) != -1:
            param['elbow_touch'] = is_elbow_touch_leg(keypoints, param['scale']) or is_elbow_pass_knee(keypoints, param['scale'])
        if is_elbow_pass_knee(keypoints, param['scale']) != -1:
            param['elbow_pass'] = is_elbow_pass_knee(keypoints, param['scale'])

        if len(param['state_total']) > 1:
            param['updown_delta'] = round(param['k_processed'][-1][5][1] - param['k_processed'][-2][5][1])
            # print(param['updown_delta'], keypoints[1][1], param['k_processed'][-1][1][1])
            param['angle_delta'] = round(get_angle_back_horizontal(param['k_processed'][-1]) - get_angle_back_horizontal(param['k_processed'][-2]))
        param['state_total'].append((param['ground'], param['back_horizontal'], param['arm_open'], param['elbow_touch'],
                                     param['elbow_pass'], param['shoulder2ground'], param['updown_delta'],
                                     param['begin_flag'], param['end_flag'], param['angle_delta']))

        # 判定坐立，只会进入一次
        if len(param['state_total']) >= 5:
            if sum(x[7] == 1 for x in param['state_total'][-5:]) >= 3 and param['began'] == -1:  # param['begin_flag'] == 1
                param['began'] = 1
                param['begin_time'] = param['i'] - 3
                logger.info("检测到准备动作")

        if len(param['state_total']) >= 20:
            if param['began'] == 1 and param['ended'] == -1:
                if param['sit_motion'] == 0:
                    param['up_start'], param['down_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)
                else:
                    param['down_start'], param['up_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.sit_motion_judgement(param)

            # 判定站起，只会进入一次
            # print(sum(x[8] == 1 for x in param['state_total'][-10:]))
            if sum(x[8] == 1 for x in param['state_total'][-5:]) >= 3 and param['ended'] == -1 \
                    and param['began'] == 1 and param['i'] - param['begin_time'] >= 2*20:  # 开始后的前2秒不计结束
                param['ended'] = 1
                param['end_time'] = param['i'] - 3
                logger.info("检测到违停动作")

            if param['began'] == 1 and param['ended'] == 1:
                # print(param['down_end'], param['up_start'])
                # if param['down_end'] - param['up_start'] > 10:
                #     param['up_start'], param['down_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)

                if param['up_start'] != -1:
                    if param['down_end'] == -1:
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
                    param['sit_up_start'] = -1

                # if param['down_end'] == -1:
                #     param['wrong_dict'] = self.update_wrong_dict(param, round(param['i'] / param['fps'], 1),
                #                                                 round(param['i'] / param['fps'], 1), [-3])  # 输出停止信息
            if param['began'] == 1 and param['ended'] == 1:
                # print(param['down_end'], param['up_start'])
                # if param['down_end'] - param['up_start'] > 10:
                #     param['up_start'], param['down_end'], param['count_including_wrong'], param['count'], param['wrong_dict'] = self.motion_judgement(param)

                if param['sit_motion'] == 0:
                    if param['up_start'] != -1:
                        if param['down_end'] == -1:
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
                else:
                    if param['down_start'] != -1 and param['up_end'] != -1:  # 下降、上升均检测到时，才判断最后一个动作

                        wrong_list = []
                        wrong_list = self.is_sit_motion_right(param, wrong_list)

                        param['count_including_wrong'] += 1
                        if len(wrong_list) == 0:
                            param['count'] += 1
                        # print(wrong_list)
                        param['wrong_dict'] = self.update_wrong_dict(param, round(param['down_start'] / param['fps'], 1),
                                                                     round(param['up_end'] / param['fps'], 1), wrong_list)

                        logger.info("动作编号： {}  ({},{})    错误列表： {}".format(param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))
                        param['total_list'].append((param['count_including_wrong'], param['down_start'], param['up_end'], wrong_list))

                        param['down_start'] = -1
                        param['up_end'] = -1

                    # if param['up_end'] == -1:
                    #     param['wrong_dict'] = self.update_wrong_dict(param, round(param['i'] / param['fps'], 1),
                    #                                                 round(param['i'] / param['fps'], 1), [-3])  # 输出停止信息

            # if count != 0:  # 防止处于非准备状态时输出一堆0
            #     total_count.append(count)
            #     count = 0

            # param['back_horizontal'] = 0
            # param['arm_open'] = 0
            # param['elbow_touch'] = 0
            # param['elbow_pass'] = 0
            # param['shoulder2ground'] = 0
        return param, frame

    def put_text(self, param, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'count: {}/{}    Level {}'.format(str(param['count']), str(param['count_including_wrong']),
                                                             str(param['level'])), (0, 15), font, 1.2 / 2, (255, 255, 0), 2)
        cv2.putText(frame, 'angle_back_horizontal: ' + str(param['angle_back_horizontal']), (0, 40), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'arm_open: ' + str(param['arm_open']), (0, 55), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'elbow_touch: ' + str(param['elbow_touch']), (0, 70), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'elbow_pass: ' + str(param['elbow_pass']), (0, 85), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'shoulder2ground: ' + str(round(param['shoulder2ground'])), (0, 100), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_flag/end_flag: ' + str(param['begin_flag']) + str(param['end_flag']), (0, 115), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'begin_time/end_time: ' + str(param['begin_time']) + str(param['end_time']), (0, 130), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'i: ' + str(param['i']), (0, 145), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'time: ' + str(round(param['i'] / param['fps'], 1)) + 's', (0, 160), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'updown_delta: ' + str(param['updown_delta']), (0, 175), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'angle_delta: ' + str(param['angle_delta']), (0, 190), font, 1.0 / 2, (0, 0, 255), 2)
        cv2.putText(frame, 'down_start/up_end: ' + str(param['down_start']) + str(param['up_end']), (0, 205), font, 1.0/2, (0, 0, 255), 2)

        return frame


# if __name__ == '__main__':
#     file_name = sys.argv[1]
#     difficulty_level = sys.argv[2]
#     frameNum = sys.argv[3]
#     outputFile = sys.argv[4]
#     deviceId = int(sys.argv[5])
#     iii = time.time()
#     cSitup = CNvSitup(file_name, difficulty_level, frameNum, outputFile, deviceId)
#     cSitup.init()
#     sss = time.time()

#     cSitup.start()
#     while not cSitup.isTailed():
#         cparam = cSitup.processAction()
#     # encode.encode_frames(cSitup.param_dict['video'], file_name, 20)
#     logger.info("{} {}", cSitup.param_dict['count'], cSitup.param_dict['count_including_wrong'])
#     logger.info(cSitup.param_dict['total_list'])
#     # draw_state(cSitup.param_dict['state_total'], [0], file_name)
#     cSitup.releaseSelf()
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
    cSitup = CNvSitup()
    mmm = time.time()
    cSitup.init()
    cSitup.start(file_name, difficulty_level, frameNum, outputFile, deviceId)
    i = 0
    while not cSitup.isTailed():
        # cPushup.stop()
        cparam = cSitup.processAction()
        logging.debug(f"i={i},cparam={cparam}")
        # cPushup.stop()#实际是控制往队列里面存数据，不是让算法结束
        i+=1
        # break
        
    # encode.encode_frames(cPushup.param_dict['video'], file_name, 20)
    logger.info("{} {}", cSitup.param_dict['count'], cSitup.param_dict['count_including_wrong'])
    logger.info("{}", cSitup.param_dict['total_list'])
    # draw_kp_2d(cPushup.param_dict['k_origin'], cPushup.param_dict['k_processed'], file_name)
    # draw_state(cPushup.param_dict['state_total'], [0], file_name)
    # for i in range(len(cPushup.param_dict['state_total'])):
    #     print(cPushup.param_dict['state_total'][i][7])
    cSitup.releaseSelf()
    # print("__init__:", round(mmm-iii, 4), "\ninit:", round(sss-mmm, 4), "\nstart:", round(xxx-sss, 4), "\nwhile:", round(yyy-xxx, 4), round(ttt-sss, 4))
