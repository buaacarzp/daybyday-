import sys 
# sys.stdout.flush()
# reply = input()
# sys.stderr.write('Parent got: "%s"\n' % reply)#stderr没有绑定到管道上

print ('Hello 2 from parent')
sys.stdout.flush()
reply = sys.stdin.readline()#另外一种方式获得子进程返回信息
sys.stderr.write('Parent got: "%s"\n' % reply[:-1]) 