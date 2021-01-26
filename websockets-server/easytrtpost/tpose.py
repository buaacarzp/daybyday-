import json
import trt_pose.coco
import trt_pose.models
import torch
import torch2trt
from torch2trt import TRTModule
import time
from loguru import logger
import sys
from cv2 import cv2
import torchvision.transforms as transforms
import PIL.Image
from trt_pose.draw_objects import DrawObjects
from trt_pose.parse_objects import ParseObjects
import argparse
import os
from cal_utils import *


class TPose:

    def __init__(self):
        try:
            # 创建topology tensor，它描述关节/部位的连结/亲和关系以及每个连结相关联的关键点
            with open('/home/jp/trt_pose/tasks/human_pose/human_pose.json', 'r') as f:
                human_pose = json.load(f)
            self.topology = trt_pose.coco.coco_category_to_topology(human_pose)
            num_parts = len(human_pose['keypoints'])
            num_links = len(human_pose['skeleton'])

            # 命令行参数可指定模型。默认使用精度更高的densenet。
            MODEL_WEIGHTS = '/home/jp/trt_pose/tasks/human_pose/densenet121_baseline_att_256x256_B_epoch_160.pth'
            OPTIMIZED_MODEL = '/home/jp/trt_pose/tasks/human_pose/densenet121_baseline_att_256x256_B_epoch_160_trt.pth'
            model = trt_pose.models.densenet121_baseline_att(num_parts, 2 * num_links).cuda().eval()
            self.MODEL_WIDTH = 256
            self.MODEL_HEIGHT = 256

            # MODEL_WEIGHTS = '/home/jp/trt_pose/tasks/human_pose/resnet18_baseline_att_224x224_A_epoch_249.pth'
            # OPTIMIZED_MODEL = '/home/jp/trt_pose/tasks/human_pose/resnet18_baseline_att_224x224_A_epoch_249_trt.pth'
            # model = trt_pose.models.resnet18_baseline_att(num_parts, 2 * num_links).cuda().eval()
            # self.MODEL_WIDTH = 224
            # self.MODEL_HEIGHT = 224

            # parser = argparse.ArgumentParser(description='TensorRT pose estimation run')
            # parser.add_argument('--model', type=str, default='densenet', help='resnet or densenet')
            # args = parser.parse_args()
            # if 'resnet' in args.model:
            #     # print('------ model  resnet--------')
            #     MODEL_WEIGHTS = '/home/jp/trt_pose/tasks/human_pose/resnet18_baseline_att_224x224_A_epoch_249.pth'
            #     OPTIMIZED_MODEL = '/home/jp/trt_pose/tasks/human_pose/resnet18_baseline_att_224x224_A_epoch_249_trt.pth'
            #     model = trt_pose.models.resnet18_baseline_att(num_parts, 2 * num_links).cuda().eval()
            #     self.MODEL_WIDTH = 224
            #     self.MODEL_HEIGHT = 224
            # else:
            #     # print('------ model  densenet-------')
            #     MODEL_WEIGHTS = '/home/jp/trt_pose/tasks/human_pose/densenet121_baseline_att_256x256_B_epoch_160.pth'
            #     OPTIMIZED_MODEL = '/home/jp/trt_pose/tasks/human_pose/densenet121_baseline_att_256x256_B_epoch_160_trt.pth'
            #     model = trt_pose.models.densenet121_baseline_att(num_parts, 2 * num_links).cuda().eval()
            #     self.MODEL_WIDTH = 256
            #     self.MODEL_HEIGHT = 256

            data = torch.zeros((1, 3, self.MODEL_HEIGHT, self.MODEL_WIDTH)).cuda()  # data测试fps
            if not os.path.exists(OPTIMIZED_MODEL):  # 判断是否需要重新通过TensorRT生成优化模型
                model.load_state_dict(torch.load(MODEL_WEIGHTS))
                self.model_trt = torch2trt.torch2trt(model, [data], fp16_mode=True, max_workspace_size=1 << 25)
                torch.save(self.model_trt.state_dict(), OPTIMIZED_MODEL)

            # 通过torch2trt载入优化模型
            self.model_trt = TRTModule()
            self.model_trt.load_state_dict(torch.load(OPTIMIZED_MODEL))

            # # benchmark the model in FPS
            # t0 = time.time()
            # torch.cuda.current_stream().synchronize()
            # for i in range(50):
            #     y = model_trt(data)
            # torch.cuda.current_stream().synchronize()
            # t1 = time.time()
            # print(50.0 / (t1 - t0))

            self.device = torch.device('cuda')

            self.parse_objects = ParseObjects(self.topology)
            self.draw_objects = DrawObjects(self.topology)

            self.kpoints = []
        except Exception as e:
            logger.error("tpose模型初始化错误")
            logger.error(e)
            raise e  # 抛异常给init函数

    def preprocess(self, imgae):
        """图片预处理，原始格式为BGR8/HWC

        """
        mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()  # Returns a copy of this object in CUDA memory.
        std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
        image = cv2.cvtColor(imgae, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self.device)
        image.sub_(mean[:, None, None]).div_(std[:, None, None])
        return image[None, ...]

    def parse_keypoints(self, objects, object_count, normalized_peaks, input_frame_width, input_frame_height):
        """
        hnum: 0 based human index
        kpoint : keypoints (float type range : 0.0 ~ 1.0 ==> later multiply by image width, height
        """
        # check invalid human index
        kpoint = []
        human = objects[0][object_count]
        C = human.shape[0]
        for j in range(C):
            k = int(human[j])
            if k >= 0:
                peak = normalized_peaks[0][j][k]  # peak[1]:width, peak[0]:height
                # 3点：peak与x、y坐标相反；坐标对应像素，此处直接处理为int；返回原分辨率对应的坐标。
                # 仿照openpose格式，坐标后跟置信度（未实现，目前为0/1）
                peak = [round(float(peak[1])*input_frame_width), round(float(peak[0])*input_frame_height), 1]
                # assert (peak[1] > 1 or peak[0] > 1)
                kpoint.append(peak)
                # print('index:%d : success [%5.3f, %5.3f]'%(j, peak[1], peak[2]) )
            else:
                peak = [0, 0, 0]
                kpoint.append(peak)
                # print('index:%d : None %d'%(j, k))
        return kpoint

    def get_keypoints(self, img):
        """返回图像上检测到的所有人的坐标的列表；可能为空列表，表示未检测到人"""
        color = (0, 255, 0)
        input_frame_height, input_frame_width, channel = img.shape
        # 图像大小必须与模型的输入大小一致
        img = cv2.resize(img, dsize=(self.MODEL_WIDTH, self.MODEL_HEIGHT), interpolation=cv2.INTER_AREA)
        data = self.preprocess(img)
        cmap, paf = self.model_trt(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()  # Returns a new Tensor, detached from the current graph.The result will never require gradient.
        object_counts, objects, normalized_peaks = self.parse_objects(cmap, paf)
        # self.draw_objects(img, object_counts, objects, normalized_peaks)
        # fps = 1.0 / (time.time() - t)
        keypoints = []
        # print(object_counts[0])
        counts = object_counts[0]
        for i in range(counts):
            # 初步筛选人员，不计关键点个数小于2的（counts未像预期那样返回正确的人数，而是包含有很多只有几个孤点的object）。
            kp_none_zero_num = sum(x != -1 for x in objects[0][i])
            if kp_none_zero_num <= 2:
                continue
            keypoint1obj = self.parse_keypoints(objects, i, normalized_peaks, input_frame_width, input_frame_height)
            keypoint1obj = self.convert_to_keypoints_body25(keypoint1obj)
            keypoints.append(keypoint1obj)
        if len(keypoints) == 0:
            return []
        # 在preconsumer中选择唯一的人；在data_process中处理0值。
        return keypoints  # 包含所有人的坐标的列表

    def convert_to_keypoints_body25(self, keypoints):
        kp = [(0, 0), (1, 17), (2, 6), (3, 8), (4, 10), (5, 5), (6, 7), (7, 9),  # (BODY25, COCO)
              (8, 8), (9, 12), (10, 14), (11, 16), (12, 11), (13, 13), (14, 15), (15, 2), (16, 1), (17, 4), (18, 3)]
        keypoints_converted = []
        for i in range(19):  # COCO18+1
            keypoints_converted.append(keypoints[kp[i][1]])
            if i == 8:  # 8点重新赋值。9或者12的缺失都会极大地影响8点，因此在使用前需先对9、12点进行填补处理。
                if keypoints[11][2]*keypoints[12][2] == 0:
                    keypoints_converted[8] = [0, 0, 0]
                else:
                    keypoints_converted[8] = [round((keypoints[11][0] + keypoints[12][0])/2), round((keypoints[11][1] + keypoints[12][1])/2), 1]
        # print(keypoints_converted[9], keypoints_converted[12])
        return keypoints_converted

    def execute(self, img):
        ttt = time.time()
        color = (0, 255, 0)
        data = self.preprocess(img)
        cmap, paf = self.model_trt(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()  # Returns a new Tensor, detached from the current graph.The result will never require gradient.
        object_counts, objects, normalized_peaks = self.parse_objects(cmap, paf)
        self.draw_objects(frame, object_counts, objects, normalized_peaks)
        fps = 1.0 / (time.time() - ttt)
        cv2.putText(frame, "FPS: %f" % fps, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)


if __name__ == "__main__":
    cap = cv2.VideoCapture("/home/jp/trt_pose/tasks/human_pose/0000.mp4")
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out_video = cv2.VideoWriter('/home/jp/trt_pose/tasks/human_pose/output.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))
    tp = TPose()
    while cap.isOpened():
        sss = time.time()
        ret, frame = cap.read()
        if not ret:
            logger.info("Camera read Over")
            break

        frame = cv2.resize(frame, dsize=(tp.MODEL_WIDTH, tp.MODEL_HEIGHT), interpolation=cv2.INTER_AREA)
        tp.execute(frame)
        out_video.write(frame)
        # key = tp.get_keypoints(frame)
        # print(len(key))
        # print(key)
        cv2.imshow("fff", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    out_video.release()
    cv2.destroyAllWindows()
