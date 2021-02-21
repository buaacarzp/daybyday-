import logging 
#本模块为高级编程

#记录器
logger = logging.getLogger('cn.applog.cccb')
logger.setLevel(logging.DEBUG) #设置日志输出级别

# 处理器handler1
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)

# 处理器handler2
fileHandler = logging.FileHandler(filename = 'demo1.log')
fileHandler.setLevel(logging.INFO)

# 定义formatter
#-8s为字符串左对齐格式化
formatter = logging.Formatter("%(asctime)s|%(levelname)-8s|%(filename)s:%(lineno)s|%(message)s")

# 给处理器设置格式
consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

# 记录器要设置处理器
logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)


#定义一个过滤器
#以记录器(笔的名字)进行过滤,但作用于处理器
flt = logging.Filter('cn.cccb')
# logger.addFilter(flt)
fileHandler.addFilter(flt)

# 打印日志
logger.debug("debug")
logger.warning("warning")
