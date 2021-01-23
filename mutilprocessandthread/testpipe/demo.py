# coding=utf-8
#使用高版本的print与除法
from __future__ import print_function
from __future__ import division
from multiprocessing import Pipe, Process
'''
https://zhuanlan.zhihu.com/p/24883194
'''

def son_process(x, pipe):
    _out_pipe, _in_pipe = pipe

    # 关闭fork过来的输入端
    _in_pipe.close()
    while True:
        try:
            msg = _out_pipe.recv()
            print ("rec:",msg)
        except EOFError:
            # 当out_pipe接受不到输出的时候且输入被关闭的时候，会抛出EORFError，可以捕获并且退出子进程
            break


if __name__ == '__main__':
    out_pipe, in_pipe = Pipe(True)
    son_p = Process(target=son_process, args=(100, (out_pipe, in_pipe)))
    son_p.start()

    # 等 pipe 被 fork 后，关闭主进程的输出端
    # 这样，创建的Pipe一端连接着主进程的输入，一端连接着子进程的输出口
    out_pipe.close()
    for x in range(10):
        in_pipe.send(x)
        print("send:",x)
    print("发送完")
    in_pipe.close()
    son_p.join()
    print ("主进程也结束了")