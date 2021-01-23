
import cv2 
from threading import Thread
import queue as tqueue
from multiprocessing import Process,Lock,Queue,Manager
import time 
# cap1_src, cap1_obj :原视频路径,保存视频的路径
cap1_src, cap1_obj = "video.mp4", "./video1.mp4"
cap2_src, cap2_obj = "video_.mp4", "./video2.mp4"
cap1 = cv2.VideoCapture(cap1_src)
cap2 = cv2.VideoCapture(cap2_src)
lock = Lock()
import time
def write_img(caps,file_names):
    '''
    单进程可以在外部序列化，这点毋庸置疑
    '''
    for cap,file_name in zip(caps,file_names):
        print("{} is handling...".format(file_name))
        WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        FPS = cap.get(cv2.CAP_PROP_FPS)
        print("FPS=",FPS)
        video_writer = cv2.VideoWriter(file_name,cv2.VideoWriter_fourcc(*"XVID"),FPS,(WIDTH,HEIGHT))
        while cap.isOpened():
            is_opened,frame = cap.read()
            if not is_opened:break
            # frame = cv2.resize(frame,(WIDTH,HEIGHT))
            video_writer.write(frame)
        cap.release()
        video_writer.release()
        print("{} is handling over.".format(file_name))

def write_img1(cap_name,file_name):
    '''
    多进程中由于不能传入序列化对象，所以此处在函数内部序列化
    '''
    cap = cv2.VideoCapture(cap_name)
    WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_writer = cv2.VideoWriter(file_name,cv2.VideoWriter_fourcc(*"H264"),30,(WIDTH,HEIGHT))
    while cap.isOpened():
        is_opened,frame = cap.read()
        if not is_opened:break
        frame = cv2.resize(frame,(WIDTH,HEIGHT))
        video_writer.write(frame)
    cap.release()
    video_writer.release()

def Multi_process():
    ts = [Process(target=write_img1,args=(cap1_src,cap1_obj)),
          Process(target=write_img1,args=(cap2_src,cap2_obj))]
    for t in ts:
        t.start()
    for j in ts:
        j.join()
def Multi_thread():
    ts = [Thread(target=write_img1,args=(cap1_src,cap1_obj)),
          Thread(target=write_img1,args=(cap2_src,cap2_obj))]
    for t in ts:
        t.start()
    for j in ts:
        j.join()

class A(Process):
    def __init__(self,cap_name,file_name):
        Process.__init__(self)
        self.cap_name,self.file_name = cap_name,file_name
    def run(self):
        with lock:
            cap = cv2.VideoCapture(self.cap_name)
            WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_writer = cv2.VideoWriter(self.file_name,cv2.VideoWriter_fourcc(*"XVID"),30,(WIDTH,HEIGHT))
            while cap.isOpened():
                is_opened,frame = cap.read()
                if not is_opened:break
                # frame = cv2.resize(frame,(WIDTH,HEIGHT))
                video_writer.write(frame)
            cap.release()
            video_writer.release()
        
#TUDO 继承方法同样不能传入一个对象
class B(Process):
    '''
    不能传入一个序列化对象
    '''
    def __init__(self,cap_name,file_name):
        Process.__init__(self)
        self.cap ,self.file_name = cap_name,file_name
    def run(self):
        with lock:
            WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_writer = cv2.VideoWriter(self.file_name,cv2.VideoWriter_fourcc(*"XVID"),30,(WIDTH,HEIGHT))
            while cap.isOpened():
                is_opened,frame = self.cap.read()
                if not is_opened:break
                # frame = cv2.resize(frame,(WIDTH,HEIGHT))
                video_writer.write(frame)
            self.cap.release()
            video_writer.release()
def put_img(cap_name,file_name,queue):    
    cap = cv2.VideoCapture(cap_name)
    cnt = 0 
    start = time.time()
    while cap.isOpened():
        is_opened,frame = cap.read()
        if not is_opened:break
        queue.put(frame)
        # print("send ",cnt)
        cnt +=1
    print("send end")
    cap.release()
    
    
def get_img(queue,file_name,WIDTH,HEIGHT):
    
    video_writer = cv2.VideoWriter(file_name,cv2.VideoWriter_fourcc(*"XVID"),30,(WIDTH,HEIGHT))
    error_cnt = 0
    cnt = 0 
    while 1:
        #如果取的速度快于放的速度，那么程序就终止了
        if queue.qsize()>0:
            frame = queue.get()
            # print("receive",cnt)
            cnt +=1
            video_writer.write(frame)
        else:
            if error_cnt>1000000:
                print("接收端提前终止")
                break
            error_cnt +=1
    video_writer.release()
    print("receive end")

def Multiprocess_get_put():
    '''
    多进程队列通信
    '''
    queue = Queue(maxsize=5)
    put_process = Process(target=put_img,args=(cap1_src,cap1_obj,queue))
    get_process = Process(target=get_img,args=(queue,cap1_obj,1920,1080))
    put_process.start()
    get_process.start()
    put_process.join()
    #如果一直等待数据，则无法退出，因为没有报出receive end 
    get_process.join()
    print("程序结束")
    # get_process.close()
def MultiThread_get_put():
    '''
    多线程队列通信
    '''
    queue = tqueue.Queue(maxsize=5)
    put_process = Thread(target=put_img,args=(cap1_src,cap1_obj,queue))
    get_process = Thread(target=get_img,args=(queue,cap1_obj,1920,1080))
    put_process.start()
    get_process.start()
    put_process.join()
    #如果一直等待数据，则无法退出，因为没有报出receive end 
    get_process.join()
    print("程序结束")
    # get_process.close()



if __name__=="__main__":
    # s = time.time()
    # Multiprocess_get_put()
    # print("多进程:",time.time() -s )
    s = time.time()
    write_img([cap1],[cap1_obj])
    print("单进程",time.time()-s)
    s = time.time()
    MultiThread_get_put()
    print("多线程",time.time()-s)

    

    
