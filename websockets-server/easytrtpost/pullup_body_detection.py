from cal_utils import *
import math
import numpy as np


def is_body_move(keypoints, scale):
    """检测身体中心线移动

    :param scale: 比例尺
    :param keypoints:
    :return:
    """
    flag = 0
    for i in [1, 4, 7, 8]:  # 若未检测到关键点，直接返回
        # if keypoints[i][0] * keypoints[i][1] < 1:
        if keypoints[i][2] < 0.05:
            return -1

    # 用4、7的中垂线为基准计算距离
    # p1 = ((np.array(keypoints[4]) + np.array(keypoints[7])) / 2).tolist()
    # k, b = get_linear_equation_coefficients(keypoints[4], keypoints[7])
    # if k == 0:
    #     p2 = [p1[0], p1[1] + 10]
    # elif math.isinf(k):  # 4、7一般是接近水平的，所以通常不会出现这种情形
    #     p2 = [p1[0] + 10, p1[1]]
    # else:
    #     p2 = [p1[0] + 10, k * (p1[0] + 10) + b]
    # length1 = scale * point2line_distance(keypoints[1], p1, p2)
    # length8 = scale * point2line_distance(keypoints[8], p1, p2)

    # 直接用横坐标x计算距离
    x_mid = (keypoints[4][0] + keypoints[7][0]) / 2
    length1 = scale * abs(keypoints[1][0] - x_mid)
    length8 = scale * abs(keypoints[8][0] - x_mid)
    # print(length1, length8)
    if length1 > 20 or length8 > 20:  # 身体移动20cm，1、8点偏离中点的距离
        flag = 1
    return flag

