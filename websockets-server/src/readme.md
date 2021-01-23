1.websockets是阻塞式的，对于客户端来说，发送给服务端一个请求后若没有得到回复，那么客户端将不会再次请求。
```
async def main_logic(web_socket,path):
    while True:
        msg = await LogicdueRecvmsg(web_socket)
        if not msg:#阻塞的
            await send_msg(web_socket,msg) 
```
在上面的代码中，我错误的将msg为None的时候才发送，这会导致客户端没有收到服务端返回的数据导致不会再次请求响应。
2.由于服务端阻塞式的原因，当客户端发送1004报文的时候，即使没有返回值，也要等，因此统一用0来处理.
3.需要解决当客户端没有请求的时候服务端异常报错的bug：
```
Traceback (most recent call last):
  File "D:\Anaconda\lib\site-packages\websockets\server.py", line 191, in handler
    await self.ws_handler(self, path)
  File "server.py", line 38, in main_logic
    msg = await LogicdueRecvmsg(web_socket)
  File "server.py", line 11, in LogicdueRecvmsg
    msg = await web_socket.recv()
  File "D:\Anaconda\lib\site-packages\websockets\protocol.py", line 509, in recv
    await self.ensure_open()
  File "D:\Anaconda\lib\site-packages\websockets\protocol.py", line 812, in ensure_open
    raise self.connection_closed_exc()
websockets.exceptions.ConnectionClosedOK: code = 1000 (OK), no reason
```
结果：查看源码后发现这是正常的现象，因为返回的是closedOk code =1000，成功捕获异常后发现CPU反而占用资源更多：
```
async def main_logic(web_socket,path):
    while True:
        # try:
        msg = await LogicdueRecvmsg(web_socket)
        if msg:#阻塞的
            await send_msg(web_socket,msg) 
        else:
            print("服务端待发送数据异常!")
        # except websockets.exceptions.ConnectionClosedOK :
        #     # print("code 10000")
        #     ...
```