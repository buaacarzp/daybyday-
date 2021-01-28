from cal_utils import *


def is_begin(keypoints):
    """检测是否站立于起终点线

    :param keypoints:
    :return:
    """
    # tag = 0
    # for p in keypoints:  # 若未检测到关键点，直接返回
    #     if tag == 1:
    #         break
    #     if p[2] < 0.05:
    #         continue
    #     else:
    #         tag = 1
    # if tag == 0:
    #     return -1

    flag = 0
    for p in [keypoints[1], keypoints[8], keypoints[11], keypoints[14]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            flag = -1

    dis111 = points_distance(keypoints[1], keypoints[11])
    dis114 = points_distance(keypoints[1], keypoints[14])
    if dis111 > 360/2 or dis114 > 360/2:  # 视频高度一半
        flag = 1
    else:
        flag = 0
    
    if keypoints[1][0] < 640/4 or keypoints[8][0] < 640/4:  # 视频宽度1/4
        flag = 1
    else:
        flag = 0

    return flag


def is_end(keypoints):
    """

    :param keypoints:
    :return:
    """
    # flag = 0
    # for p in [keypoints[4], keypoints[7], keypoints[1], keypoints[8]]:  # 若未检测到关键点，直接返回
    #     # if p[0] * p[1] < 1:
    #     if p[2] < 0.05:
    #         return -1
    # bar = (keypoints[1][1] + keypoints[8][1]) / 2
    # if (keypoints[4][1] + keypoints[7][1]) / 2 > bar or keypoints[4][1] > bar or keypoints[7][1] > bar:
    #     flag = 1

    # return flag

    flag = 0
    for p in [keypoints[1], keypoints[8], keypoints[11], keypoints[14]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            flag = -1

    dis111 = points_distance(keypoints[1], keypoints[11])
    dis114 = points_distance(keypoints[1], keypoints[14])
    if dis111 > 360/2 or dis114 > 360/2:  # 视频高度一半
        flag = 1
    else:
        flag = 0
    
    if keypoints[1][0] > 640*0.75 or keypoints[8][0] > 640*0.75:  # 视频宽度1/4
        flag = 1
    else:
        flag = 0

    return flag


def is_foot_behind_line(keypoints):
    for p in [keypoints[11], keypoints[14]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1

    # if keypoints[11][1] > 270*0.875 and keypoints[14][1] > 270*0.875:
    if keypoints[11][1] > 360**0.75 and keypoints[14][1] > 360**0.75:  # 起终点线位于视频底部1/4
        return 1
    else:
        return 0
