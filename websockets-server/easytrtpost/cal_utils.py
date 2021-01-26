import copy
import math
import numpy as np


def get_line_cross_angle(k11, k12, k21, k22):
    """
    计算点k11/k12组成的直线与点k21/k22组成的直线的夹角
    :param k11: [x,y]
    :param k12: [x,y]
    :param k21: [x,y]
    :param k22: [x,y]
    :return:
    """
    vector_a = np.array([(k12[0] - k11[0]), (k12[1] - k11[1])])  # 向量a
    vector_b = np.array([(k22[0] - k21[0]), (k22[1] - k21[1])])  # 向量a
    cos_value = (float(vector_a.dot(vector_b)) / (
            np.sqrt(vector_a.dot(vector_a)) * np.sqrt(vector_b.dot(vector_b))))  # 转成浮点数运算，cosθ=a·b/|a||b|，[-1,1]
    # print(cos_value)
    return np.rad2deg(np.arccos(round(cos_value, 3)))  # 两个向量的夹角[0, pi]， 余弦值：cos_value


def points_distance(k1, k2):
    """
    计算两点距离
    :param k1: [x,y]
    :param k2: [x,y]
    :return:
    """
    dis = math.sqrt(math.pow(k1[0] - k2[0], 2) + math.pow(k1[1] - k2[1], 2))
    return dis


def point2line_distance(p1, l1, l2):
    """
    计算点p1到过点l1、l2的直线的距离
    :param p1: [x,y]
    :param l1: [x,y]
    :param l2: [x,y]
    :return:
    """
    px, py = p1[0:2]
    l1x, l1y = l1[0:2]
    l2x, l2y = l2[0:2]
    # 计算直线方程AX+BY+C=0
    A = l2y - py
    B = px - l2x
    C = l2x * py - px * l2y
    # 计算点到直线的距离
    distance = np.array(abs(A * l1x + B * l1y + C)) / np.array(math.sqrt(A * A + B * B))
    return distance


def get_linear_equation_coefficients(p1, p2):
    """

    :param p1:
    :param p2:
    :return:
    """
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    # y=kx+b
    if x1 == x2:
        return float('inf'), x1
    else:
        k = (y1 - y2) / (x1 - x2)
        b = y2 - (y1 - y2) * x2 / (x1 - x2)
        return k, b


def is_point_above_line(p, l1, l2):
    """点是否位于直线以上。

    :param p:
    :param l1:
    :param l2:
    :return:
    """

    k, b = get_linear_equation_coefficients(l1, l2)
    if not math.isinf(k):
        if k * p[0] + b < p[1]:
            return True
        else:
            return False
    else:
        if b < p[0]:
            return True
        else:
            return False


def get_length_scale(p1, p2, length):
    """1像素代表的实际长度cm

    :param p1:
    :param p2:
    :param length: 实际长度
    :return:
    """
    for p in [p1, p2]:  # 若未检测到关键点，直接返回
        # if p[0] * p[1] < 1:
        if p[2] < 0.05:
            return -1.
    return np.array(length) / np.array(points_distance(p1, p2))


def kp_moving_status(k_processed, kp_index):
    """检测指定的点的运动状态(以最近6帧计算)

    :param k_processed:
    :param kp_index: 要检测的点的索引
    :return:
    """
    updown_delta = []
    kp_base = 0
    # 计算6个updown_delta
    for i in range(7):
        if k_processed[i-7][kp_index][2] < 0.05:
            updown_delta.append(0)
            continue
        else:
            if kp_base == 0:
                updown_delta.append(0)
                kp_base = k_processed[i-7][kp_index][1]
                continue
            else:
                delta = k_processed[i-7][kp_index][1] - kp_base
                updown_delta.append(delta)
                kp_base = k_processed[i-7][kp_index][1]

    # if sum(x < -4 for x in updown_delta) > 4 and sum(x for x in updown_delta) < -20:
    #     return 1  # 上升
    # elif sum(x > 4 for x in updown_delta) > 4 and sum(x for x in updown_delta) > 20:
    #     return 0  # 下降
    # else:
    #     return -1  # 稳定

    if sum(x for x in updown_delta) < -20:
        return 1  # 上升
    elif sum(x for x in updown_delta) > 20:
        return 0  # 下降
    else:
        return -1  # 稳定


def is_pull_up(k_processed):
    """

    :param k_processed:
    :return:
    """
    # print(kp_moving_status(k_processed, 1), kp_moving_status(k_processed, 8), kp_moving_status(k_processed, 11), kp_moving_status(k_processed, 14))
    if (kp_moving_status(k_processed, 1) == 1 or kp_moving_status(k_processed, 8) == 1) \
            and (kp_moving_status(k_processed, 11) == 1 or kp_moving_status(k_processed, 14) == 1):
        return 1
    else:
        return 0


def is_pull_down(k_processed):
    """

    :param k_processed:
    :return:
    """
    if (kp_moving_status(k_processed, 1) == 0 or kp_moving_status(k_processed, 8) == 0) \
            and (kp_moving_status(k_processed, 11) == 0 or kp_moving_status(k_processed, 14) == 0):
        return 1
    else:
        return 0


def data_process_prev(keypoints, k_origin, k_processed, vheight, processed_num):
    """

    :param keypoints: 当前帧关键点
    :param k_origin:
    :param k_processed: 各帧处理后的关键点
    :param vheight:
    :param processed_num:
    :return:
    """
    # print(keypoints)
    if len(k_processed) < 5:
        return keypoints, processed_num
    for i in range(19):
        index = 0  # 不为0的最近帧
        for j in range(5):  # 只取最近5帧，太旧的帧没有意义
            # if k_processed[j][i][0] * k_processed[j][i][1] > 1:
            if k_processed[-j-1][i][2] >= 0.05:
                index = -j-1
                break
        if index != 0:  # 最近5帧都是0值则不处理当前帧的关键点的i点
            # if keypoints[i][0] * keypoints[i][1] > 1:
            if processed_num[i] <= 1:  # 对于某个点，连续处理的帧数不能超过5帧
                processed_num[i] = 5
                continue
            if keypoints[i][2] >= 0.05:  # 非0值
                # key_mean = sum(x for x in k_) / len(k_)  #
                # print(key_mean)
                # if points_distance(k_processed[index][i], keypoints[i]) > 0.07 * vheight:  # 与最近帧上对应的点的距离，视频高度的0.07
                #     if k_origin[index][i][0] == k_processed[index][i][0] and k_origin[index][i][1] == k_processed[index][i][1]:
                #         keypoints[i] = copy.deepcopy(k_processed[index][i] + 0.07 * (keypoints[i] - k_processed[index][i]))
                #     else:
                #         # 通过区分最近帧是否处理过来处理当前帧，效果不明显
                #         keypoints[i] = copy.deepcopy(k_processed[index][i] + 0.07 * (keypoints[i] - k_processed[index][i]))
                # pass  # 非0异常值处理效果不好：关键点更新“滞后”
                if is_kp_shift(keypoints[i], k_processed[index][i], abs(index)) == 1:  # 漂移点处理
                    keypoints[i] = k_processed[index][i]
                    processed_num[i] -= 1
                else:
                    processed_num[i] = 5
            else:  # 0值
                if sum(x[2] > 0.05 for x in keypoints) >= 10:  # 非0值点超过10个才对其他点作0值填充处理
                    keypoints[i] = k_processed[index][i]
                    processed_num[i] -= 1
        else:
            processed_num[i] = 5
    # print(keypoints)
    return keypoints, processed_num


def data_process(keypoints, k_origin, k_processed, vheight, processed_num):
    """

    :param keypoints: 当前帧关键点
    :param k_origin:
    :param k_processed: 
    :param vheight:
    :param processed_num:
    :return:
    """
    # print(keypoints)
    if len(k_processed) < 5:
        return keypoints, processed_num
    # 从骨骼长度方面处理异常点
    process_skeleton_too_long(keypoints)

    for i in range(19):
        if keypoints[i][2] >= 0.05:  # 先判断离群点，置0处理
            # if processed_num[i] > 1:
            if is_kp_shift(keypoints, keypoints[i], k_processed[-1][i]) == 1:
                keypoints[i] = [0, 0, 0]
        if keypoints[i][2] < 0.05:  # 0值填充处理
            if processed_num[i] > 1:
                keypoints[i] = k_processed[-1][i]
                processed_num[i] -= 1
        else:
            processed_num[i] = 5

    return keypoints, processed_num


def process_skeleton_too_long(keypoints):
    skeleton = [[0, 1, (0, 0, 255)], [1, 8, (0, 0, 255)],  # 红
                [1, 2, (0, 255, 255)], [2, 3, (0, 255, 255)], [3, 4, (0, 255, 255)],  # 黄
                [1, 5, (255, 0, 255)], [5, 6, (255, 0, 255)], [6, 7, (255, 0, 255)],  # 粉
                [8, 9, (255, 255, 255)], [9, 10, (255, 255, 255)], [10, 11, (255, 255, 255)],  # 白色
                [8, 12, (255, 255, 0)], [12, 13, (255, 255, 0)], [13, 14, (255, 255, 0)]]  # 蓝
    for x in skeleton:
        if keypoints[x[0]][0]*keypoints[x[0]][1] >= 0.05 and keypoints[x[1]][0]*keypoints[x[1]][1] >= 0.05:  # 不处理0值点
            if points_distance(keypoints[x[0]], keypoints[x[1]]) > 200:  # 超过200则关键点置0
                keypoints[x[0]] = [0, 0, 0]
                keypoints[x[1]] = [0, 0, 0]


def is_kp_shift(keypoints, kp, previous_kp):
    """点漂移的像素距离

    :param kp:
    :param previous_kp:
    :return:
    """
    if previous_kp[0] * previous_kp[1] == 0:  # 前一帧为0值则视当前帧为正常点
        return 0
    if points_distance(kp, previous_kp) > 50:
        return 1
    else:
        return 0


def select_kp(keypoints, rtsp_width, rtsp_height):
    """若有多个人员，选择画面中心/比例scale最大/关键点最全/距离画面中心最近的那个"""
    # len(keypoints) >= 1
    compute_result = []
    for i in range(len(keypoints)):
        is_center, max_dis, dis_c2c = compute_person_scale(keypoints[i], rtsp_width, rtsp_height)
        kp_none_zero_num = sum(x[2] != 0 for x in keypoints[i])
        compute_result.append((is_center, max_dis, kp_none_zero_num, dis_c2c))

    compute_result = np.array(compute_result)
    score = []  # is_center计1.5分，其余0.5
    for i in range(len(keypoints)):
        score.append(compute_result[i][0])  # is_center计分
    for i in np.argmax(compute_result, axis=0):  # axis轴上每一项中最大值的索引
        if compute_result[i][1] == 0:  # 人的最长边为0
            return []
        if i > 0:  # 其他3项计分
            score[i] += 0.5

    if len(score) != 0:
        index = score.index(max([x for x in score]))
        return [keypoints[index]]  # 包含不大于一个人的坐标的列表
    else:
        return []


def compute_person_scale(keypoints, rtsp_width, rtsp_height):
    """修改自openpose-->personTracker.cpp-->computePersonScale"""
    if len(keypoints) == 0:
        return 0.0, 0.0, 640.0
    # 关键点分为4层
    layer_count = 0
    if sum(x[0]*x[1] != 0 for x in [keypoints[0], keypoints[15], keypoints[16], keypoints[17], keypoints[18]]):
        layer_count += 1
    if sum(x[0]*x[1] != 0 for x in [keypoints[2], keypoints[3], keypoints[4], keypoints[5], keypoints[6], keypoints[7]]):
        layer_count += 1
    if sum(x[0]*x[1] != 0 for x in [keypoints[8], keypoints[11]]):
        layer_count += 1
    if sum(x[0]*x[1] != 0 for x in [keypoints[10], keypoints[11], keypoints[13], keypoints[14]]):
        layer_count += 1
    if layer_count == 0:
        return 0.0, 0.0, 640.0
    # 寻找目标矩形框的长边
    min_x = rtsp_width
    max_x = 0
    min_y = rtsp_height
    max_y = 0
    for i in range(len(keypoints)):
        kk = keypoints[i]
        if kk[0]*kk[1] != 0:
            if kk[0] < min_x:
                min_x = kk[0]
            if kk[0] > max_x:
                max_x = kk[0]
            if kk[1] < min_y:
                min_y = kk[1]
            if kk[1] > max_y:
                max_y = kk[1]
    is_center = 0.0  # 是否位于画面中心
    if min_x < rtsp_width/2 < max_x and min_y < rtsp_height/2 < max_y:
        is_center = 1.5
    dis_c2c = points_distance([(min_x+max_x)/2, (min_y+max_y)/2], [rtsp_width/2, rtsp_height/2])  # 目标框中心点到画面中心点的距离
    x_dist = max_x - min_x
    y_dist = max_y - min_y
    if x_dist > y_dist:
        max_dist = x_dist*4/np.array(layer_count)  # 长边长度。layer_count需不为0，必须保证传入的keypoints不为空
    else:
        max_dist = y_dist*4/np.array(layer_count)

    return is_center, max_dist, dis_c2c
