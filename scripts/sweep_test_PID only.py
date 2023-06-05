"""Test and plot the input and output voltage of the interferometer. """
#Standard imports:
from bitstring import BitArray
import matplotlib.pyplot as plt
#Self written imports:
from startup_pc_mcu import start_pc_mcu

voltage = []
voltage1 = []
time = []
packetsize = 10240

confirm, ser = start_pc_mcu("COM5")

for i in range(1):
    message = ser.read(2*packetsize)
    message_bits = BitArray(message)
    for j in range(packetsize):
        message_bytes = message_bits[0+j*16:(j+1)*16]
        voltage.append(message_bytes.int/4095.0*3.3)


for i in range(1):
    message = ser.read(2*packetsize)
    message_bits = BitArray(message)
    for j in range(packetsize):
        message_bytes = message_bits[0+j*16:(j+1)*16]
        voltage1.append(message_bytes.int/4095.0*3.3)


for i in range(1):
    message = ser.read(4*packetsize)
    message_bits = BitArray(message)
    for j in range(packetsize):
        message_bytes = message_bits[0+j*32:(j+1)*32]
        time.append(message_bytes.int*0.001)

plt.plot(time, voltage, label = "Received output from interferometer")
plt.plot(time, voltage1, label = "Send input to interferometer")
plt.ylim([-0.5,3.5])
plt.ylabel("Voltage [V]")
plt.xlabel("Time [S]")
plt.legend()
plt.title("Feedback response")
plt.show()
