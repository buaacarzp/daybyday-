import re 
rtsp = "rtsp://admin:admin12345@192.168.1.124/cam/realmonitor?channel=1&subtype=0"
ip_str = re.findall("\\d+\\.\\d+\\.\\d+\\.\\d+", rtsp)
print(ip_str)