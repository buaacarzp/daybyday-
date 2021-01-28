from cal_utils import *


def is_begin(keypoints):
    """检测是否坐立：8点低于13点、14/8与水平线夹角小于45度。

    :param keypoints:
    :return:
    """
    # flag = 0
    for p in [keypoints[8], keypoints[13], keypoints[14]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    
    theta148 = get_line_cross_angle(keypoints[14], keypoints[8], keypoints[14], [keypoints[14][0] + 2, keypoints[14][1]])
    # theta138 = get_line_cross_angle(keypoints[13], keypoints[8], keypoints[13], [keypoints[13][0] + 2, keypoints[13][1]])
    if keypoints[8][1] > keypoints[13][1] and theta148 < 45:  # 8点低于13点，并且14、8角度小于45度
        return 1
    else:
        return 0


def is_end(keypoints):
    """

    :param keypoints:
    :return:
    """
    # flag = 0
    # for p in [keypoints[13], keypoints[8]]:  # 若未检测到关键点，直接返回
    #     # if p[0] * p[1] < 1:
    #     if p[2] < 0.05:
    #         return -1
    # if keypoints[8][1] < keypoints[13][1]:  #
    #     flag = 1

    # return flag

    # if is_begin(keypoints) == 1:
    #     return 0
    # else:
    #     return 1

    for p in [keypoints[8], keypoints[13], keypoints[14]]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1

    theta148 = get_line_cross_angle(keypoints[14], keypoints[8], keypoints[14], [keypoints[14][0] + 2, keypoints[14][1]])
    # theta138 = get_line_cross_angle(keypoints[13], keypoints[8], keypoints[13], [keypoints[13][0] + 2, keypoints[13][1]])
    if keypoints[8][1] < keypoints[13][1] and theta148 > 45:  # 8点低于13点，并且14、8角度小于45度
        return 1
    else:
        return 0
