def is_head_pass(keypoints):
    """检测头部是否过杠

    :param keypoints:
    :return:
    """
    for i in [0, 1, 4, 7]:  # 若未检测到关键点，直接返回
        # if keypoints[i][0] * keypoints[i][1] < 1:
        if keypoints[i][2] < 0.05:
            return -1

    y_bar = (keypoints[4][1] + keypoints[7][1]) / 2  # 单杠的高度按左右手（4、7）点位高度的平均值为准
    y_mandible = (keypoints[0][1] + keypoints[1][1]) / 2  # 下颌的位置

    if y_mandible < y_bar:  # 下颌的位置高于单杠的位置（坐标小于）
        return 1
    else:
        return 0


def is_nose_pass(keypoints):
    """

    :param keypoints:
    :return:
    """
    for i in [0, 4, 7]:  # 若未检测到关键点，直接返回
        # if keypoints[i][0] * keypoints[i][1] < 1:
        if keypoints[i][2] < 0.05:
            return -1

    y_bar = (keypoints[4][1] + keypoints[7][1]) / 2  # 单杠的高度按左右手（4、7）点位高度的平均值为准
    y_nose = keypoints[0][1]   #

    if y_nose < y_bar:  # 位置高于单杠的位置（坐标小于）
        return 1
    else:
        return 0
