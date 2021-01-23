#coding=utf-8
#https://www.cnblogs.com/guapitomjoy/archive/2004/01/13/11515567.html
import os, time, sys

mypid = os.getpid()
parentpid = os.getppid()
sys.stderr.write('child %d of %d got arg: "%s"\n' %(mypid, parentpid, sys.argv[1]))

for i in range(2):
    time.sleep(3)
    recv = input()#从管道获取数据,来源于父经常stdout
    time.sleep(3)
    send = 'Child %d got: [%s]' % (mypid, recv)
    print(send)#stdout绑定到管道上,发送到父进程stdin
    sys.stdout.flush()