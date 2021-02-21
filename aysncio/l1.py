import asyncio
from greenlet import greenlet
def func1():
    print(1)
    print(2)
def func2():
    print(3)
    print(4)
if __name__ =="__main__":
    func1()
    func2()

def gen():
    print('z')
    for i in range(100):
        print('s')
        yield i 
gen()