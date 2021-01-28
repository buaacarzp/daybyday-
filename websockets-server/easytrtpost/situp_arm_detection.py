from cal_utils import *


def is_arm_open(keypoints, scale):
    """检测手臂是否抱于胸前

    :param max_arm_length_r:
    :param max_arm_length:
    :param keypoints:
    :param scale:
    :return:
    """
    p1, p2, p3, p4, p5, p6, p7, p8 = keypoints[1:9]

    # for p in keypoints[5:8]:  # 用右臂2、3、4代替，否则返回
    #     # if p[0] * p[1] < 1:
    #     if p[2] < 0.05:
    #         for q in keypoints[2:5]:
    #             # if q[0] * q[1] < 1:
    #             if q[2] < 0.05:
    #                 return -1
    #         dis423 = point2line_distance(p4, p2, p3)
    #         if dis423 > max_arm_length_r * 0.6:  # 另一侧手臂只用4点检测，3点位置没有特点
    #             # print('youyouyou', dis423, max_arm_length_r)
    #             return 1
    #         else:
    #             return 0

    # dis756 = point2line_distance(p7, p5, p6)
    # dis618 = point2line_distance(p6, p1, p8)
    # # 判断6、7两点的位置
    # if dis756 > max_arm_length * 0.6 and dis618 > max_arm_length * 0.4 and is_point_above_line(p6, p1, p8):
    #     # print('zuozuozuo', dis756, dis618, max_arm_length, is_point_above_line(p6, p1, p8))
    #     # print(keypoints[1], keypoints[5:9])
    #     return 1
    # else:
    #     return 0

    for p in [p5, p6, p7]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    
    theta = get_line_cross_angle(p6, p5, p6, p7)
    length = points_distance(p6, p7) * scale
    # print(length, theta)
    if length > 0.5 * 30 and theta >= 145:  # 在前臂长度大于一半上臂长度的情况下，才判断
        return 1
    else:
        return 0


def is_elbow_pass_knee(keypoints, scale):
    flag = 0
    for p in [keypoints[6], keypoints[13]]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    # if is_point_above_line(keypoints[6], keypoints[12], keypoints[13]):
    #     flag = 1
    if keypoints[6][0] <= keypoints[13][0]+20:  # 13点右侧一定范围内以左
        flag = 1

    # theta81 = get_line_cross_angle(keypoints[8], keypoints[1], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]])
    # theta5618 = get_line_cross_angle(keypoints[5], keypoints[6], keypoints[1], keypoints[8])
    # if theta81 >= 90: # and theta5618 >= 45:
    #     flag = 1
    dis = points_distance(keypoints[6], keypoints[13])
    # print(dis*scale)
    if dis * scale <= 20:  # 小于20cm同样视为过膝
        flag = 1
    return flag


def is_elbow_touch_leg(keypoints, scale):
    flag = 0
    for p in [keypoints[6], keypoints[12], keypoints[13]]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    dis = point2line_distance(keypoints[6], keypoints[12], keypoints[13])
    # print(dis * scale)
    if keypoints[6][0] < keypoints[12][0]+20:  # 位于12点右侧一定距离时一定不能触腿，避免直线距离的误判
        if dis * scale < 20 or is_point_above_line(keypoints[6], keypoints[12], keypoints[13]):  # 20cm
            flag = 1
    return flag


def get_arm_length(p1, p2):
    """上臂长度

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

