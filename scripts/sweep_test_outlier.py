"""Test and plot the input and output voltage of the interferometer. """
#Standard imports:
from bitstring import BitArray
import matplotlib.pyplot as plt
import math
import numpy as np
#Self written imports:
from startup_pc_mcu import start_pc_mcu

voltage = []
voltage1 = []
voltage2 = []
time = []
time1 = []
time2 = []
outlier = []
median = []
outlierdata = []
outliertime = []
packetsize = 256
percentage = 20

confirm, ser = start_pc_mcu("COM5")

message = ser.read(2*packetsize)
message_bits = BitArray(message)
for j in range(packetsize):
    message_bytes = message_bits[0+j*16:(j+1)*16]
    voltage.append(message_bytes.int/4095.0*3.3)

message = ser.read(4*packetsize)
message_bits = BitArray(message)
for j in range(packetsize):
    message_bytes = message_bits[0+j*32:(j+1)*32]
    time.append(message_bytes.int*0.001)

for i in range(2):
    message = ser.read(2*math.floor(packetsize*percentage/100))
    message_bits = BitArray(message)
    for j in range(math.floor(packetsize*percentage/100)):
        message_bytes = message_bits[0+j*16:(j+1)*16]
        voltage1.append(message_bytes.int/4095.0*3.3)

    message = ser.read(4*math.floor(packetsize*percentage/100))
    message_bits = BitArray(message)
    for j in range(math.floor(packetsize*percentage/100)):
        message_bytes = message_bits[0+j*32:(j+1)*32]
        time1.append(message_bytes.int*0.001)

    message = ser.read(2)
    message_bits = BitArray(message)
    median.append(message_bits.int/4095.0*3.3)

message = ser.read(2*packetsize)
message_bits = BitArray(message)
for j in range(packetsize):
    message_bytes = message_bits[0+j*16:(j+1)*16]
    print(message_bytes.int)
    outlier.append(message_bytes.int)

message = ser.read(2*packetsize)
message_bits = BitArray(message)
for j in range(packetsize):
    message_bytes = message_bits[0+j*16:(j+1)*16]
    voltage2.append(message_bytes.int/4095.0*3.3)

message = ser.read(4*packetsize)
message_bits = BitArray(message)
for j in range(packetsize):
    message_bytes = message_bits[0+j*32:(j+1)*32]
    time2.append(message_bytes.int*0.001)

#Remove all the outliers:
#create list of indexes that have to be removed:
indexes = []
for i in range(len(outlier)):
    if outlier[i] == 1:
        indexes.append(i)

for i in indexes:
    outlierdata.append(voltage2[i])
    outliertime.append(time2[i])

time3 = np.array(time2)
voltage3 = np.array(voltage2)

time2 = np.delete(time3, indexes)
voltage2 = np.delete(voltage3, indexes)


fig, (ax1, ax2, ax3) = plt.subplots(3)
ax1.plot(time, voltage, label = "Received output from interferometer")
ax1.legend()
ax2.scatter(time1, voltage1, label = "bottom/top 10%", marker = 'o')
ax2.axhline(y = median[0], label = "median top 10%", color = "r", linestyle = 'dashed')
ax2.axhline(y = median[1], label = "median bottom 10%", color = "g", linestyle = 'dashed')
ax2.legend()
ax3.scatter(time2, voltage2, label = "sorted received output from interferometer")
ax3.scatter(outliertime, outlierdata, label = "outliers", color = "r")
ax3.legend()

plt.setp(ax1, ylim=(-0.5,3.5))
plt.setp(ax2, ylim=(-0.5,3.5))
plt.xlim([0,packetsize*0.001])
plt.ylabel("Voltage [V]")
plt.xlabel("Time [S]")
plt.show()
