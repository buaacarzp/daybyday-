from cal_utils import *


def is_arm_straight(keypoints):
    """检测手臂是否伸直

    :param keypoints:
    :return:
    """
    flag = 0
    p2, p3, p4, p5, p6, p7 = keypoints[2:8]

    for p in keypoints[2:5]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            for q in keypoints[5:8]:
                # if q[0] * q[1] < 1:
                if q[2] < 0.05:
                    return -1  # 若未检测到关键点，直接返回
                else:  # 用另一只手臂检测
                    theta = get_line_cross_angle(p6, p5, p6, p7)
                    # print(theta)
                    if theta > 145:  # 上、前臂夹角大于145°视为伸直
                        flag = 1
                    return flag

    theta = get_line_cross_angle(p3, p2, p3, p4)
    # print(theta)
    if theta > 125:
        flag = 1
    return flag


def is_shoulder_up(keypoints, max_arm_length):
    """辅助判断手臂伸直

    :param keypoints:
    :param max_arm_length:
    :return:
    """
    flag = 0
    for p in [keypoints[2], keypoints[3], keypoints[4]]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:  # 若未检测到关键点，直接返回
            return -1
    # print('手臂长度', points_distance(keypoints[4], keypoints[2]), max_arm_length)
    if points_distance(keypoints[2], keypoints[4]) > max_arm_length * 0.8:
        flag = 1
    return flag


def is_shoulder_below_elbow(keypoints):
    for p in [keypoints[2], keypoints[3]]:
        if p[2] < 0.05:
            return -1
    if keypoints[2][1] > keypoints[3][1]:
        return 1
    else:
        return 0


def get_arm_total_length(keypoints):
    """上、前臂长度

    :param keypoints:
    :return:
    """

    for p in [keypoints[2], keypoints[3], keypoints[4]]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1.
    dis23 = points_distance(keypoints[2], keypoints[3])
    dis34 = points_distance(keypoints[3], keypoints[4])
    dis24 = points_distance(keypoints[2], keypoints[4])
    # print(dis24, dis23+dis34)
    return dis23+dis34


def get_ground_coordinate(keypoints, scale):
    """4、7纵坐标近似地面位置

    :param keypoints:
    :return:
    """
    ground = -1.

    # for p in [keypoints[4], keypoints[7]]:
    #     # if p[0] * p[1] < 1:
    #     if p[2] < 0.05:
    #         return -1.
    #
    # ground = (keypoints[4][1] + keypoints[7][1]) / 2
    # for p in [keypoints[3], keypoints[4], keypoints[11]]:
    #     # if p[0] * p[1] < 1:
    #     if p[2] < 0.05:
    #         return -1.

    # ground = (keypoints[3][1] + 2 * keypoints[4][1] + keypoints[11][1]) / 4
    # if points_distance(keypoints[3], keypoints[4]) * scale > 15:
    #     ground = keypoints[3][1] + 0.6 * (keypoints[4][1] - keypoints[3][1])
    # elif keypoints[3][1] < keypoints[4][1] < keypoints[11][1]:
    #     ground = (keypoints[4][1] + keypoints[11][1]) / 2
    # if points_distance(keypoints[3], keypoints[4]) * scale > 15:
    #     ground = keypoints[3][1] + 0.6 * (keypoints[4][1] - keypoints[3][1])
    # ground1 = (keypoints[4][1] + keypoints[11][1]) / 2
    # ground2 = keypoints[3][1] + 0.6 * (keypoints[4][1] - keypoints[3][1])
    # ground = (ground1+ground2)/2
    if keypoints[4][2] < 0.05:
        return -1.
    if keypoints[3][2] < 0.05:
        if keypoints[11][2] >= 0.05:
            ground = (keypoints[4][1] + keypoints[11][1]) / 2
            return ground
        else:
            return -1.
    if keypoints[11][2] < 0.05:
        if keypoints[3][2] >= 0.05:
            if points_distance(keypoints[3], keypoints[4]) * scale > 15:
                ground = keypoints[3][1] + 0.6 * (keypoints[4][1] - keypoints[3][1])
                return ground
            else:
                return -1.
        else:
            return -1.
    ground1 = (keypoints[4][1] + keypoints[11][1]) / 2
    ground2 = keypoints[3][1] + 0.6 * (keypoints[4][1] - keypoints[3][1]) if points_distance(keypoints[3], keypoints[4]) * scale > 15 else ground1
    ground = (ground1+ground2)/2
    return ground
