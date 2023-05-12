import time 
from serial import Serial

ser = Serial(port="COM7", baudrate=115200)

# ser.open()

while 1:
    print(ser.read())
    time.sleep(1)

