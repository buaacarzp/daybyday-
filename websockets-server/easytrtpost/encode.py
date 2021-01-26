import subprocess
import random
import time
import re
from cv2 import cv2

# controls the quality of the encode
# CRF_VALUE = '21'

# h.264 profile
# PROFILE = 'baseline'

# encoding speed:compression ratio
PRESET = 'veryfast'

# path to ffmpeg bin
FFMPEG_PATH = '/usr/bin/ffmpeg'


def encode_file(file_name):
    output = file_name.split('.')[0] + str(random.randint(1, 1000)) + ".mp4"

    command = [
        FFMPEG_PATH, '-i', file_name, '-y', '-c:v', 'libx264', '-preset', PRESET,
    ]
    # command = [
    #     FFMPEG_PATH, '-i', file,
    #     '-y', '-c:v', 'libx264', '-preset', PRESET, '-profile:v', PROFILE, '-crf', CRF_VALUE,
    # ]
    command += ['-c:a', 'copy']  # if audio is using AAC copy it - else encode it
    command += ['-threads', '8', output]  # add threads and output
    subprocess.call(command)  # encode the video!


def encode_frames(frames, file_name, fps):
    """opencv获取的frames写入pipe，ffmpeg读取并转码

    :param fps: 原视频帧率
    :param frames:
    :param file_name: 生成文件名
    :return:
    """
    output = ""
    if "://" in file_name:
        output = re.findall("\\d+\\.\\d+\\.\\d+\\.\\d+", file_name)
        output = output[0] + time.strftime("-%Y%m%d%H%M%S") + ".mp4"
    elif "/" in file_name:
        output = re.split("/|\\.", file_name)[-2] + str(random.randint(1, 1000)) + ".mp4"
    else:
        output = file_name.split('.')[0] + str(random.randint(1, 1000)) + ".mp4"

    output = "/home/jp/trt_pose/tasks/human_pose/video/{}".format(output)
    try:
        height, width, channel = frames[0].shape
    except Exception as e:
        print("获取图像失败/编码图片数组空")
        print(e)
        raise e

    ffmpeg = 'ffmpeg'
    dimension = '{}x{}'.format(width, height)

    command = [ffmpeg,
               '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-s', dimension,
               '-pix_fmt', 'bgr24',  # OpenCV uses bgr format
               '-r', str(fps),
               '-i', '-',
               '-an',
               '-c:v', 'libx264',
               '-preset', 'veryfast',
               '-pix_fmt', 'yuv420p',
               # '-profile:v', 'baseline',
               # '-level', '1.3',
               # '-tune:v', 'none',
               # '-crf', '23.0',
               # '-b:v', '5000k',
               output]

    sp = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=2**12)

    for frame in frames:
        sp.stdin.write(frame.tostring())

    sp.stdin.close()
    sp.stderr.close()
    sp.wait()
