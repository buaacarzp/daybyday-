以俯卧撑为例：
cPushup = CNvPushup(file_name, difficulty_level, frameNum, outputFile, deviceId)

1. rtsp视频流地址
2. 考核等级（一般为5，暂时不用其他等级）
3. 考核时长（以帧数计，一般为2分钟，fps为20，总时长2400祯，目前考虑多录2s，即为2440帧）
4. 视频保存路径（/usr/local/tnkhxt/files/video/xxx.mp4）
5. GPU序号（已弃用但保留了相关接口，传整数0即可）

Note:
2021-1-27 
1.完成修改了逻辑，修改basetype类
2.完成添加后端正常关闭异常捕捉
3.完成尝试每次返回
```
def Pose_Assessment_start2222(self,recv_dict):
        '''
        input: dict
        output: dict
        '''
        while not self.cPushup.isTailed():
            self.cparam = self.cPushup.processAction()
            print("self.cparam=",self.cparam)
        print("处理完的结果为:",self.cPushup.param_dict['count'], self.cPushup.param_dict['count_including_wrong'])
        return {}
```
4.TUDO：姿态考核停止要能触发开始的停止，但是目前没有这么写
5.TUDO：添加logging写入正在运行的程序
2021-1-28
1.完成修改了basetype返回是dict，不是json
2.添加了debug模式，用于调试
3.将五个检测整合在了一起,但是发现了已知的问题当服务端长时间发送会导致客户端主动断开连接,可能需要会滚版本查看之前的是否支持长时间发送.
server
```
2021-01-28 19:43:33,769,ERROR,2021-01-28 19:43:33,769,server.py:193:Error in connection handler
Traceback (most recent call last):
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/server.py", line 191, in handler
    await self.ws_handler(self, path)
  File "src/server.py", line 72, in main_logic
    await send_msg(web_socket,Utils.pack(msg[1],gen))#这里是模拟真实数据
  File "src/server.py", line 60, in send_msg
    await web_socket.send(msg)
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 567, in send
    await self.write_frame(True, opcode, data)
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 1083, in write_frame
    await self.ensure_open()
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 803, in ensure_open
    raise self.connection_closed_exc()
websockets.exceptions.ConnectionClosedError: code = 1006 (connection closed abnormally [internal]), no reason

```
cilent:
```
Traceback (most recent call last):
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 827, in transfer_data
    message = await self.read_message()
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 895, in read_message
    frame = await self.read_data_frame(max_size=self.max_size)
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 971, in read_data_frame
    frame = await self.read_frame(max_size)
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 1051, in read_frame
    extensions=self.extensions,
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/framing.py", line 105, in read
    data = await reader(2)
  File "/usr/lib/python3.6/asyncio/streams.py", line 674, in readexactly
    yield from self._wait_for_data('readexactly')
  File "/usr/lib/python3.6/asyncio/streams.py", line 464, in _wait_for_data
    yield from self._waiter
concurrent.futures._base.CancelledError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "cilent_rtsp.py", line 49, in <module>
    loop.run_until_complete(main_logic(ip))
  File "/usr/lib/python3.6/asyncio/base_events.py", line 484, in run_until_complete
    return future.result()
  File "cilent_rtsp.py", line 28, in main_logic
    await recv_msg(websocket)
  File "cilent_rtsp.py", line 14, in recv_msg
    msg = await websocket.recv()
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 509, in recv
    await self.ensure_open()
  File "/home/jp/.local/lib/python3.6/site-packages/websockets/protocol.py", line 812, in ensure_open
    raise self.connection_closed_exc()
websockets.exceptions.ConnectionClosedError: code = 1006 (connection closed abnormally [internal]), no reason

```