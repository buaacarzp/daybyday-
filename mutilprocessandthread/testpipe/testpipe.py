from multiprocessing import Process,Pipe
'''
pipe obj:
    recv()
    send()
    close()
process obj:
    start()
    join()
    
'''
def send(x,node):
    sendnode,recnode = node 
    print(id(sendnode))
    recnode.close()
    for i in range(10):
        sendnode.send(i)
        print("send",i)
    sendnode.close()    
def send2(x,sendnode,recnode):
    # sendnode,recnode = node 
    print(id(sendnode))
    recnode.close()
    for i in range(10):
        sendnode.send(i)
        print("send",i)
    sendnode.close()        
    

def rec(x,node):
    sendnode,recnode = node 
    sendnode.close()
    while 1:
        try:
            msg = recnode.recv()
            print("receive",msg)
        except EOFError:
            # 当out_pipe接受不到输出的时候且输入被关闭的时候，会抛出EORFError，可以捕获并且退出子进程
            recnode.close()
            break

    
if __name__ =="__main__":
    conn1, conn2 = Pipe(True)
    # print(id(conn1))
    # send_process = Process(target=send1,args=(100,conn1,conn2))
    receive_process = Process(target=rec,args=(100,(conn1,conn2)))
    # send_process.start()
    receive_process.start()
    #----
    conn2.close()
    for i in range(10):
        conn1.send(i)
        print("send",i)
    conn1.close()   #不关闭发送会一直发
    #------
    # send_process.join()
    receive_process.join()
    print("发送与结束结束")