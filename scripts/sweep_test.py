"""Test and plot the input and output voltage of the interferometer. """
#Standard imports:
from time import sleep
from bitstring import BitArray
import matplotlib.pyplot as plt
#Self written imports:
from startup_pc_mcu import start_pc_mcu

voltage = []
packetsize = 80

confirm, ser = start_pc_mcu("COM5")

for i in range(16):
    message = ser.read(2*packetsize)
    message_bits = BitArray(message)
    for j in range(packetsize):
        message_bytes = message_bits[0+j*16:(j+1)*16]
        voltage.append(message_bytes.int/4095.0*3.3)
        print(message_bytes)
    sleep(0.001)

plt.plot(voltage)
plt.ylim([-0.5,3.5])
plt.show()
