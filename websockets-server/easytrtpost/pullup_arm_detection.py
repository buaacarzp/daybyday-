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
    if theta > 145:  # 上、前臂夹角大于145°视为伸直
        flag = 1
    return flag


def get_arm_length(keypoints):
    """前臂长度

    :param keypoints:
    :return:
    """
    p3, p4 = keypoints[3:5]
    p6, p7 = keypoints[6:8]

    for p in [p3, p4]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            # 计算6到7的距离
            for q in [p6, p7]:  # 若未检测到关键点，直接返回
                # if q[0] * q[1] < 1:
                if q[2] < 0.05:
                    return -1.
            dis67 = points_distance(p6, p7)
            return dis67
    # 计算3到4的距离
    dis34 = points_distance(p3, p4)
    return dis34
