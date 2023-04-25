#!/usr/bin/python3
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt

from scipy import signal 
from scipy.fft import fft, ifft, fftfreq

def generate_sine(freq, sample_rate, duration): 
    x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    frequencies = x * freq
    # 2pi because np.sin takes radians
    y = np.sin((2 * np.pi) * frequencies)
    return x, y

# create random transferfunction 
num = np.array([1 ,0.5 ,0.5]) # np.random.rand(1,3)
den = np.array([1 ,0.3 ,0.6])# np.random.rand(1,3)
random_TF = signal.TransferFunction(num, den)

# Generate sine 
t = np.linspace(0, 100, 500)
f = 100
f_s = 10_000
duration = 1
x, y = generate_sine(f,f_s, duration)

# FFT 
Y = abs(fft(y)) 
w = abs(fftfreq(x.size, 1/f_s) )

# Product of Y*TF 
output = Y*random_TF 
# plt.figure(1)
# plt.plot(x,y)
# plt.show()



# plt.figure(2)
# plt.stem(w,Y)
# plt.show() 