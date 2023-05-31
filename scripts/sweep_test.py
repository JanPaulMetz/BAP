"""Test and plot the input and output voltage of the interferometer. """
#Standard imports:
from time import sleep
from bitstring import BitArray
from serial_module import serial_init
import matplotlib.pyplot as plt
#Self written imports:
from startup_pc_mcu import start_pc_mcu

voltage = []

confirm, ser = start_pc_mcu("COM5")
# ser = serial_init("COM5")
# ser.read_all()
for i in range(256):
    message = ser.read(2)
    # print(message.decode())
    message_bits = BitArray(message)
    message_bytes = message_bits[0:16]
    voltage.append(message_bytes.int/4095.0*3.3)
    sleep(0.01)

plt.plot(voltage)
plt.axis([0,256,-0.5,3.5])
plt.show()
