from cal_utils import *
from pushup_body_detection import get_point2ground_distance


def is_foot_open(keypoints, scale):
    """

    :param scale:
    :param keypoints:
    :return:
    """
    flag = 0
    # if keypoints[11][0] * keypoints[14][0] < 1:
    #     if keypoints[11][0] * keypoints[14][0] < 1:
    if keypoints[11][2] < 0.05 or keypoints[14][2] < 0.05:
        return -1
    else:
        dis = points_distance(keypoints[11], keypoints[14])

    # 计算双脚的距离
    # if dis * scale > const.DIS_FOOT:  # 20cm
    #     # print("双脚距离大于20", dis)
    #     flag = 1
    return flag


def is_knee_on_ground(keypoints, ground, scale):
    """
    膝盖是否着地
    :param scale:
    :param ground:
    :param keypoints:
    :return:
    """
    # flag = 0
    # p10, p13 = [keypoints[10], keypoints[13]]
    # # if p10[0] * p10[1] < 1:
    # #     if p13[0] * p13[1] > 1:
    # if p10[2] < 0.05:
    #     if p13[2] > 0.05:
    #         knee = p13
    #     else:
    #         return -1
    # else:
    #     knee = p10
    # knee2ground = get_point2ground_distance(knee, ground) * scale
    # # print("膝盖距地", ground, knee2ground)
    # if knee2ground <= const.DIS_KNEE_GROUND:  # 膝盖距离地面5cm
    #     flag = 1

    # return flag

    for p in [keypoints[10], keypoints[11]]:
        if p[2] < 0.05:
            return -1
    dis1011 = points_distance(keypoints[10], keypoints[11]) * scale
    theta = get_line_cross_angle(keypoints[10], keypoints[9], keypoints[10], keypoints[11])
    # print(dis1011, theta)
    if dis1011 > 20 and theta < 150 and keypoints[10][1] > keypoints[11][1]:  # 10/11点y坐标差值大于20、大小腿夹角小于150
        return 1
    else:
        return 0
