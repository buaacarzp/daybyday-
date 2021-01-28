from cal_utils import *


def is_begin(keypoints):
    """检测手臂是否举起：4、7的位置高于3、6（坐标位置小于后者）。

    :param keypoints:
    :return:
    """
    # flag = 0
    # coefficient = (-1, -1)  # 杠面方程系数

    # for p in [keypoints[4], keypoints[7], keypoints[1], keypoints[8]]:  # 若未检测到关键点，直接返回
    #     # if p[0] * p[1] < 1:
    #     if p[2] < 0.05:
    #         flag = -1

    # bar = (keypoints[1][1] + keypoints[8][1]) / 2
    # if (keypoints[4][1] + keypoints[7][1]) / 2 < bar and keypoints[4][1] < bar and keypoints[7][1] < bar:  #
    #     flag = 1
    #     coefficient = get_linear_equation_coefficients(keypoints[4], keypoints[7])

    # begin_params = {'is_begin': flag, 'coefficient': coefficient}  # coefficient暂时没用到

    for p in [keypoints[3], keypoints[4], keypoints[6], keypoints[7]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    if keypoints[4][1] < keypoints[3][1] and keypoints[7][1] < keypoints[6][1]:
        return 1
    else:
        return 0


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

    for p in [keypoints[3], keypoints[4], keypoints[6], keypoints[7]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    if keypoints[4][1] > keypoints[3][1] and keypoints[7][1] > keypoints[6][1]:
        return 1
    else:
        return 0


def is_up(k_processed, k_index, percent):
    """

    :param k_processed: 关键点列表
    :param k_index: 关注变化的点
    :param percent: 点的变化超过1/8点距离的%
    :return:
    """
    dis18 = points_distance(k_processed[-1][1], k_processed[-1][8])
    # print(dis18)
    delta = k_processed[-1][k_index][1] - k_processed[-10][k_index][1]
    if delta < -dis18 * percent:
        return True
    else:
        return False
