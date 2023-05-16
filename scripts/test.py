"""Script to test methods"""
from time import sleep
import serial_module


ser = serial_module.serial_init("COM5")

ser.close()
ser.open()

while 1:
    print(serial_module.check_buffer_content(ser))
    sleep(1)
