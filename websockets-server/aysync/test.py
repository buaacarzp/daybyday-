# import asyncio
# async def func():
#     asyncio.sleep(3)
#     print("func")
# async def func2():
#     for i in range(1000000):
#         if i%10000==0:print(f'i={i}')

# async def superl():
#     await func()
#     await func2()
    
#     # await func()
    

# loop = asyncio.get_event_loop()
# task = [loop.create_task(superl())]
# loop.run_until_complete(asyncio.wait(task))
import asyncio
async def async_function():
    return 1

async def await_coroutine():
    result = await async_function()
    print(result)
loop = asyncio.get_event_loop()
loop.run_until_complete(await_coroutine())
loop.run_forever()
# 1