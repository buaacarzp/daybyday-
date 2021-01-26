import numpy as np

from cal_utils import *


def get_leg_length(p1, p2):
    """小腿长度

    :param p1:
    :param p2:
    :return:
    """
    for p in [p1, p2]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1.

    dis = points_distance(p1, p2)
    return dis


def get_mean_length(length_list, i):
    """

    :param length_list:
    :param i: 当前帧数
    :return:
    """
    if len(length_list) > 100:
        if i % 3 == 0:  # 大值弹出少
            max_length = max(length_list)
            max_index = length_list.index(max_length)
            length_list.pop(max_index)
        else:
            min_length = min(length_list)
            min_index = length_list.index(min_length)
            length_list.pop(min_index)
    mean_length = np.mean(np.array(length_list))

    return length_list, mean_length


def get_mean_value(value_list, i):
    """

    :param value_list:
    :param i: 当前帧数
    :return:
    """
    if len(value_list) > 100:
        if i % 2 == 0:
            max_value = max(value_list)
            max_index = value_list.index(max_value)
            value_list.pop(max_index)
        else:
            min_value = min(value_list)
            min_index = value_list.index(min_value)
            value_list.pop(min_index)
    mean_value = np.mean(np.array(value_list))

    return value_list, mean_value
