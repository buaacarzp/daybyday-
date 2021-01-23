#https://blog.csdn.net/csujiangyu/article/details/44956287
#coding=utf-8
import os, sys

def spawn(prog, *args):
    stdinFd = sys.stdin.fileno()
    stdoutFd = sys.stdout.fileno()

    parentStdin, childStdout = os.pipe()
    childStdin, parentStdout= os.pipe()
    
    pid = os.fork()
    if pid:
        os.close(childStdin)
        os.close(childStdout)
        os.dup2(parentStdin, stdinFd)#输入流绑定到管道,将输入重定向到管道一端parentStdin
        os.dup2(parentStdout, stdoutFd)#输出流绑定到管道,发送到子进程childStdin
    else:
        os.close(parentStdin)
        os.close(parentStdout)
        os.dup2(childStdin, stdinFd)#输入流绑定到管道
        os.dup2(childStdout, stdoutFd)
        args = (prog, ) + args
        os.execvp(prog, args)
        assert False, 'execvp failed!'

if __name__ == '__main__':
    mypid = os.getpid()
    spawn('python', 'pipetest.py', 'spam')

    print ('Hello 1 from parent', mypid) #打印到输出流parentStdout, 经管道发送到子进程childStdin
    sys.stdout.flush()
    reply = raw_input()
    sys.stderr.write('Parent got: "%s"\n' % reply)#stderr没有绑定到管道上

    print ('Hello 2 from parent', mypid)
    sys.stdout.flush()
    reply = sys.stdin.readline()#另外一种方式获得子进程返回信息
    sys.stderr.write('Parent got: "%s"\n' % reply[:-1]) 