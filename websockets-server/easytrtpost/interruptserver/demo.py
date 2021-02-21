#!/usr/bin/env py3

import asyncio
async def a():
    print ("a")
async def b():
    print ("b")

asyncio.ensure_future(a())
bb=asyncio.ensure_future(b())
loop = asyncio.get_event_loop()
loop.run_until_complete(bb)#虽然传入的参数是task-bb,但是task-a却会执行，
#并且是第一个执行，首先打印a,其次打印b