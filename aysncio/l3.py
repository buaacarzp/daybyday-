import asyncio
import time 
async def wiatfunc():
    time.sleep(2)
    # for i in range(100000000):
    #     ...



async def func():
    print (1)
    # await asyncio.sleep(2)
    await wiatfunc() 
    # await time.sleep(2)
    print(2)
    return "return"
async def main():
    print (" main ")
    #Create a Task object to add the current func Task to the event loop.
    task1 = asyncio.create_task (func())
    #Create a Task object to add the current func Task to the event loop.
    task2 = asyncio.create_task(func())
    print (" end of main ")
    #When the execution of a coroutine encounters 10 operation, it will automatically switch to other tasks.
    #In this case await is to wait for all corresponding coroutines to complete and get the result
    ret1 = await task1
    ret2=  await task2
    print(ret1, ret2)
asyncio.run (main())