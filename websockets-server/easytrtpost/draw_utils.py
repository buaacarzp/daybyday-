import os
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2


def draw_kp_2d(k_origin, k_processed, file):
    for key in range(19):
        x = np.arange(len(k_origin))
        y1 = np.array([value[key][0] for value in k_origin])
        y2 = np.array([value[key][1] for value in k_origin])
        plt.plot(x, y1, label='origin_x')
        plt.plot(x, y2, label='origin_y')
        y1_processed = np.array([v[key][0] for v in k_processed])
        y2_processed = np.array([v[key][1] for v in k_processed])
        plt.plot(x, y1_processed, label='processed_x')
        plt.plot(x, y2_processed, label='processed_y')
        plt.legend()

        if not os.path.exists('image'):
            os.mkdir('image')
        # if not os.path.exists('image/' + file.split('.')[0]):
        #     os.mkdir('image/' + file.split('.')[0])
        # plt.savefig("image/{}/kp_2d_{:03d}.jpg".format(file.split('.')[0], key), dpi=250, quality=100)
        plt.savefig("image/kp_2d_{:03d}.jpg".format(key), dpi=250, quality=100)
        plt.clf()
    plt.close()


def draw_kp_3d(k_origin, k_processed, file):
    ax = Axes3D(plt.figure())
    for key in range(19):
        frame = np.arange(len(k_origin))
        x = np.array([value[key][0] for value in k_origin])
        y = np.array([value[key][1] for value in k_origin])
        ax.plot(frame, x, y, label='origin')
        x_processed = np.array([value[key][0] for value in k_processed])
        y_processed = np.array([value[key][1] for value in k_processed])
        ax.plot(frame, x_processed, y_processed, label='processed')
        ax.legend()

        if not os.path.exists('image'):
            os.mkdir('image')
        # if not os.path.exists('image/' + file.split('.')[0]):
        #     os.mkdir('image/' + file.split('.')[0])
        plt.savefig("image/kp_3d_{:03d}.jpg".format(key), dpi=250, quality=100)
        ax.cla()
    plt.close()


def draw_state(state_total, index_list, file):
    x = np.arange(len(state_total))
    # y = np.array([value[0] for value in state_total])
    # plt.plot(x, y, label='ground')
    # y = np.array([value[5] for value in state_total])
    # plt.plot(x, y, label='shoulder2ground')
    # y = np.array([value[6] for value in state_total])
    # plt.plot(x, y, label='body2ground')
    for i in index_list:
        y = np.array([value[i] for value in state_total])
        plt.plot(x, y, label='ground')
    plt.legend()
    # plt.ylim(ymin=240, ymax=260)
    plt.locator_params(axis='y', nbins=25)

    if not os.path.exists('image'):
        os.mkdir('image')
    # if not os.path.exists('image/' + file.split('.')[0]):
    #     os.mkdir('image/' + file.split('.')[0])
    plt.savefig("image/state_total_{}.jpg".format(file.split('.')[0]), dpi=250, quality=100)
    plt.clf()
    plt.close()


def draw_parts(keypoints, frame):
    skeleton = [[0, 1, (0, 0, 255)], [1, 8, (0, 0, 255)],  # 红
                [1, 2, (0, 255, 255)], [2, 3, (0, 255, 255)], [3, 4, (0, 255, 255)],  # 黄
                [1, 5, (255, 0, 255)], [5, 6, (255, 0, 255)], [6, 7, (255, 0, 255)],  # 粉
                [8, 9, (255, 255, 255)], [9, 10, (255, 255, 255)], [10, 11, (255, 255, 255)],  # 白色
                [8, 12, (255, 255, 0)], [12, 13, (255, 255, 0)], [13, 14, (255, 255, 0)]]  # 蓝
    for x in skeleton:
        if keypoints[x[0]][2] >= 0.05 and keypoints[x[1]][2] > 0.05:
            cv2.line(frame, (keypoints[x[0]][0], keypoints[x[0]][1]), (keypoints[x[1]][0], keypoints[x[1]][1]), color=x[2], thickness=3)
            cv2.putText(frame, "{}".format(str(x[0])), (keypoints[x[0]][0]+5, keypoints[x[0]][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, x[2], 1)
            cv2.putText(frame, "{}".format(str(x[1])), (keypoints[x[1]][0]+5, keypoints[x[1]][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, x[2], 1)
    return frame


def draw_percent(file_name1, zero_value_percent1, std_total1, file_name2, zero_value_percent2, std_total2):
    file_name1 = file_name1.split('.')[0]
    file_name2 = file_name2.split('.')[0]
    x = np.arange(19)

    plt.plot(x, zero_value_percent1, label='0%-{}'.format(file_name1))
    plt.plot(x, zero_value_percent2, label='0%-{}'.format(file_name2))

    plt.plot(x, [i[0] for i in std_total1], label='std_x-{}'.format(file_name1))
    plt.plot(x, [i[0] for i in std_total2], label='std_x-{}'.format(file_name2))
    plt.plot(x, [i[1] for i in std_total1], label='std_y-{}'.format(file_name1))
    plt.plot(x, [i[1] for i in std_total2], label='std_y-{}'.format(file_name2))

    plt.legend()

    if not os.path.exists('image'):
        os.mkdir('image')
    plt.savefig("image/{}-{}.jpg".format(file_name1, file_name2), dpi=250, quality=100)
    plt.clf()
    plt.close()
