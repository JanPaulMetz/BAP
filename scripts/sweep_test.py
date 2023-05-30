"""Test and plot the input and output voltage of the interferometer. """
#Standard imports:
from time import sleep
from bitstring import BitArray
from serial_module import serial_init
#Self written imports:
from startup_pc_mcu import start_pc_mcu


confirm, ser = start_pc_mcu("COM5")
# ser = serial_init("COM5")
# ser.read_all()
while True:
    message = ser.read(2)
    # print(message.decode())
    message_bits = BitArray(message)
    message_bytes = message_bits[0:16]
    print(message_bytes)
    sleep(0.01)
