from cal_utils import *


def is_waist_bend(keypoints):
    """

    :param keypoints:
    :return:
    """
    flag = 0
    for p in [keypoints[2], keypoints[8], keypoints[9], keypoints[11]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1

    theta = get_line_cross_angle(keypoints[8], keypoints[2], keypoints[9], keypoints[11])
    # print(theta)
    if theta < 160 and keypoints[8][1] > keypoints[2][1] \
            and get_line_cross_angle(keypoints[8], keypoints[2], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]]) > 15:  # 8/2与水平线夹角
        # 10点在图像上位于1、8直线下面时，计算结果是位于直线上部。
        flag = 1

    return flag


def is_butt_bend(keypoints):
    """

    :param keypoints:
    :return:
    """
    flag = 0
    for p in [keypoints[2], keypoints[8], keypoints[9], keypoints[11]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1

    theta = get_line_cross_angle(keypoints[8], keypoints[2], keypoints[9], keypoints[11])
    # print(theta)
    if theta < 150 and keypoints[8][1] < keypoints[2][1] \
            and get_line_cross_angle(keypoints[8], keypoints[2], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]]) > 15:  # 8/2与水平线夹角
        flag = 1

    return flag


def get_point2ground_distance(p, ground):
    """

    :param ground:
    :param p:
    :return:
    """
    # if p[0] * p[1] < 1:
    if p[2] < 0.05:
        return -1.

    return ground - p[1]
