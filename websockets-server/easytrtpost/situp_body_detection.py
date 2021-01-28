from cal_utils import *


def select_person(keypoints, k):
    """根据坐标x大小选择人员。

    :param k:
    :param keypoints:
    :return:
    """
    # print(len(keypoints))
    if len(keypoints) == 0 or len(keypoints) > 2:  # 0人、多余2人，直接返回-1
        return -1
    elif len(keypoints) == 1:
        # if len(k) != 0:
        #     if points_distance(keypoints[0][8], k[-1][8]) > 50:  # 默认8点一定能获取到；距离大于50像素
        #         return -1
        #     else:
        #         return 0
        # else:
        #     return -1  # 针对2个人的视频，如果k_processed为空，无法比较判断，返回-1
        return 0
    elif len(keypoints) == 2:  # 根据坐标x大小选择人员
        li = []
        for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 15, 16, 17, 18]:
            # if keypoints[0][i][0] * keypoints[0][i][1] > 1 and keypoints[1][i][0] * keypoints[1][i][0] > 1:
            if keypoints[0][i][2] > 0.05 and keypoints[1][i][2] > 0.05:
                li.append(i)
        if len(li) == 0:
            return -1
        for j in li:
            if keypoints[0][j][0] > keypoints[1][j][0]:
                return 0
            else:
                return 1


def is_back_horizontal(keypoints):
    """

    :param keypoints:
    :return:
    """
    # if keypoints[1][0] * keypoints[1][1] < 1 or keypoints[8][0] * keypoints[8][1] < 1:
    if keypoints[5][2] < 0.05 or keypoints[8][2] < 0.05:
        return -1
    theta85 = get_line_cross_angle(keypoints[8], keypoints[5], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]])
    # 躺平时，可能会出现角度大于15度、1点低于8点的情况
    if theta85 < 15 or (theta85 >= 15 and keypoints[5][1] > keypoints[8][1]):  # 背与水平夹角
        return 1
    else:
        return 0


def get_angle_back_horizontal(keypoints):
    if keypoints[5][2] < 0.05 or keypoints[8][2] < 0.05:
        return -1
    theta85 = get_line_cross_angle(keypoints[8], keypoints[5], keypoints[8], [keypoints[8][0] + 2, keypoints[8][1]])
    if keypoints[5][1] > keypoints[8][1]:
        theta85 = -1 * theta85
    return round(theta85)
