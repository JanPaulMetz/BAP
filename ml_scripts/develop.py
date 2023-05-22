"""Dev """
import numpy as np
import matplotlib.pyplot as plt
from scipy import fft
from generate_data import *
import nfft

# Generete even fft
freq = 100
fs = 1000
duration = 0.1
x_even = np.linspace(0, 101, num=512)
x, y_even = generate_discrete_sine(freq, fs, duration)
print(np.shape(y_even))
plt.figure()
plt.scatter(x, y_even)
plt.show()
print(y_even.shape)
fft_even = nfft.ndft(x, y_even)
plt.figure()
plt.scatter(x, np.abs(fft_even))
plt.show()
# Generate odd fft
x_odd = np.linspace(0,101, num=512)
