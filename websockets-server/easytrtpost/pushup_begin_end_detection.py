from cal_utils import *


def is_begin(keypoints):
    """检测是否趴下：小腿、躯干与水平线夹角小于60度。

    :param keypoints:
    :return:
    """
    # flag = 0
    for p in [keypoints[2], keypoints[8], keypoints[9], keypoints[10], keypoints[11]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    # dis18 = points_distance(keypoints[1], keypoints[8])
    # if abs(keypoints[8][1] - keypoints[1][1]) < 0.707 * dis18:  # 45°
    #     flag = 1

    theta82 = get_line_cross_angle(keypoints[8], keypoints[2], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]])
    theta1110 = get_line_cross_angle(keypoints[11], keypoints[10], keypoints[11], [keypoints[11][0] + 2, keypoints[11][1]])
    dis82 = points_distance(keypoints[8], keypoints[2])
    dis109 = points_distance(keypoints[10], keypoints[9])
    dis1110 = points_distance(keypoints[11], keypoints[10])
    dis112_x = keypoints[2][0] - keypoints[11][0]
    if dis112_x >= (dis82+dis109+dis1110)*0.6:
        return 1
    else:
        return 0


def is_end(keypoints):  # 
    """

    :param keypoints:
    :return:
    """
    # flag = 0
    for p in [keypoints[2], keypoints[8], keypoints[9], keypoints[10], keypoints[11]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    # dis18 = points_distance(keypoints[1], keypoints[8])
    # if abs(keypoints[8][1] - keypoints[1][1]) > 0.707 * dis18:  # 45°
    #     flag = 1
    theta82 = get_line_cross_angle(keypoints[8], keypoints[2], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]])
    theta1110 = get_line_cross_angle(keypoints[11], keypoints[10], keypoints[11], [keypoints[11][0] + 2, keypoints[11][1]])
    dis82 = points_distance(keypoints[8], keypoints[2])
    dis109 = points_distance(keypoints[10], keypoints[9])
    dis1110 = points_distance(keypoints[11], keypoints[10])
    dis112_x = keypoints[2][0] - keypoints[11][0]
    if dis112_x < (dis82+dis109+dis1110)*0.6:
        return 1
    else:
        return 0
