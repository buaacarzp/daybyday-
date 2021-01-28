from cal_utils import *


def is_leg_open(keypoints):
    """检测双腿张开是否过大

    :param keypoints:
    :return:
    """
    flag = 0
    # 计算点9/11、12/14组成的直线的夹角
    p9, p10, p11, p12, p13, p14 = keypoints[9:15]
    for p in keypoints[9:15]:  # 若未检测到关键点，直接返回
        if p[0] * p[1] < 1:
            return -1

    theta = get_line_cross_angle(p9, p11, p12, p14)
    if theta > 30:  # 两腿夹角超过30°视为过大
        flag = 1
    # 计算9/12、10/13、11/14的距离辅助判断
    dis912 = points_distance(p9, p12)
    dis1013 = points_distance(p10, p13)
    dis1114 = points_distance(p11, p14)
    if dis912 * 1.5 < dis1013 or dis912 * 2.5 < dis1114:  # 两腿关节点张开距离因子
        flag = 1
    return flag


def is_leg_bend(keypoints):
    """检测蹬腿，即腿部是否弯曲

    :param keypoints:
    :return:
    """
    flag = 0
    p9, p10, p11, p12, p13, p14 = keypoints[9:15]
    for p in keypoints[9:15]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1
    # 计算大小腿的夹角
    theta = get_line_cross_angle(p10, p9, p10, p11)
    theta2 = get_line_cross_angle(p13, p12, p13, p14)
    # print(theta, theta2)
    if theta < 150 or theta2 < 150:  # 夹角小于150°视为弯腿
        flag = 1

    return flag


def is_leg_swing(keypoints, KEYPOINTS):
    """检测腿部摆动

    :param KEYPOINTS:
    :param keypoints:
    :return:
    """
    flag = 0
    p9, p10, p11, p12, p13, p14 = keypoints[9:15]
    P9, P10, P11, P12, P13, P14 = KEYPOINTS[9:15]

    for p in [p9, p10, p11]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            # 计算12到13、13到14的距离
            for q in [p12, p13, p14]:  # 若未检测到关键点，直接返回
                # if q[0] * q[1] < 1:
                if q[2] < 0.05:
                    return -1

            dis1213 = points_distance(p12, p13)
            dis1314 = points_distance(p13, p14)
            DIS1213 = points_distance(P12, P13)
            DIS1314 = points_distance(P13, P14)
            if (DIS1213 - dis1213) / DIS1213 > 0.4 \
                    or (DIS1314 - dis1314) / DIS1314 > 0.4:  # 腿部摆动，腿长变化比例
                # print("右边", (DIS1213 - dis1213) / DIS1213, (DIS1314 - dis1314) / DIS1314)
                # print(dis1213, DIS1213, dis1314, DIS1314)
                # 0.14：摆幅30°时计算得到，0.25自定
                flag = 1

    # 计算9到10、到11的距离
    dis911 = points_distance(p9, p10)
    DIS911 = points_distance(P9, P10)
    # dis910 = points_distance(p9, p10)
    # dis1011 = points_distance(p10, p11)
    # DIS910 = points_distance(P9, P10)
    # DIS1011 = points_distance(P10, P11)
    # if (DIS910 - dis910) / DIS910 > 0.25 or (DIS1011 - dis1011) / DIS1011 > 0.25:
    if (DIS911 - dis911) / DIS911 > 0.4:
        # print("腿长", (DIS910 - dis910) / DIS910, (DIS1011 - dis1011) / DIS1011)
        # print(dis910, DIS910, dis1011, DIS1011)
        # 0.14：摆幅30°时计算得到
        flag = 1

    return flag


def get_leg_length(keypoints):
    """腿长

    :param keypoints:
    :return:
    """
    p9, p10, p11, p12, p13, p14 = keypoints[9:15]

    for p in [p9, p10, p11]:
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            # 计算12到14的距离
            for q in [p12, p13, p14]:  # 若未检测到关键点，直接返回
                # if q[0] * q[1] < 1:
                if q[2] < 0.05:
                    return -1.
            dis1214 = points_distance(p12, p14)
            return dis1214
    # 计算9到11的距离
    dis911 = points_distance(p9, p11)
    return dis911
