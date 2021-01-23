from multiprocessing import Lock,Pipe,Process
def producer(con,pro,name,food):
    con.close()
    for i in range(100):
        f = '%s生产%s%s'%(name,food,i)
        print(f)
        pro.send(f)
    pro.send(None)
    pro.send(None)
    pro.send(None)
    pro.close()
def consumer(con,pro,name,lock):
    pro.close()
    while True:
        lock.acquire()
        food = con.recv()
        lock.release()
        if food is None:
            con.close()
            break
        print('%s吃了%s' % (name, food))
if __name__ == '__main__':
    con,pro = Pipe()
    lock= Lock()
    p = Process(target=producer,args=(con,pro,'egon','泔水'))
    c1 = Process(target=consumer, args=(con, pro, 'alex',lock))
    c2 = Process(target=consumer, args=(con, pro, 'bossjin',lock))
    c3 = Process(target=consumer, args=(con, pro, 'wusir',lock))
    c1.start()
    c2.start()
    c3.start()
    p.start()
    con.close()
    pro.close()