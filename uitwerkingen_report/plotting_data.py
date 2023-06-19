import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy import fft
import pandas as pd

file_name = 'cutoff_measurements.csv'
df = pd.read_csv(file_name)
x_data = df['X'].to_numpy()
ch1 = df['CH1'].to_numpy()
ch2 = df['CH2'].to_numpy()
start = df['Start']
print(x_data)
increment = [5e-2*int(data) for data in x_data[1:]]
ch1 = [float(data) for data in ch1[1:]]
ch2 = [float(data) for data in ch2[1:]]
print(x_data)
print(ch1)
plt.figure()
plt.plot(increment, ch1, marker='.')
plt.show()