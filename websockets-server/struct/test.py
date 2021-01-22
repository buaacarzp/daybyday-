import struct
x = int(input())
y = struct.pack("i",x)
z = struct.unpack("i",y)
print(x,y,z)