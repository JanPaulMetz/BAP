"""Script to test methods"""
from time import sleep
import serial_module

packet = bytearray()
packet.append(0x41)
packet.append(0x42)
packet.append(0x43)

ser = serial_module.serial_init("COM5") #Put the right settings.
#Make sure that the serial port is openend again:
ser.close()
ser.open()

#Empty the buffer 5 times to be sure that it is empty.
count = 0
while count<5:
    ser.read_all()
    sleep(1)
    count += 1

# TODO: Define counters :))
#Send start message to MCU.
send_count = 0
confirmation = False
while not confirmation:
    serial_module.serial_write(ser,packet)
    check_confirmation_count = 0
    while not confirmation and check_confirmation_count<5:
        sleep(0.1)
        x = serial_module.serial_read(ser)
        if x == "42":
            confirmation = True
            break
        check_confirmation_count += 1
    send_count += 1
    if send_count==5:
        raise TimeoutError('Received no confirmation of the MCU')

print("startup completed")
    #print(serial_module.serial_read(ser).decode())
    