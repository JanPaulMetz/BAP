import time 
import serial

ser = serial.Serial(port="COM5",
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE)

# ser.open()
# b = bytes()
MESSAGE = 'message'
while 1:
    ser.write((MESSAGE + '\n').encode())
    time.sleep(0.1)
    READ_LINE = ser.readline()
    SERIAL_MESSAGE = READ_LINE.decode().replace('\n','')
    print(SERIAL_MESSAGE)
    time.sleep(0.01)
