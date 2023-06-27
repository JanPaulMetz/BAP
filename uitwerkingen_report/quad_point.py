""" Quadrature point"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy import fft
import pandas as pd
alpha = 5
def sine_func(x, amplitude, frequency, phase, offset, offset_slope):
    return amplitude* np.sin(2 * np.pi * frequency * x + phase) + offset + offset_slope*x

def discrete_sine(sample_rate, frequency, num_samples):
    # Create discrete sine
    time_ax = np.arange(num_samples)/sample_rate
    signal = np.sin(2*np.pi*frequency*time_ax)
    return signal, time_ax

def first_derivative(x, amplitude, frequency, phase, offset_slope):
    return (2 * np.pi * frequency)*amplitude*np.cos(2* np.pi * frequency * x + phase) + offset_slope

def second_derivative(x, amplitude, frequency, phase):
    return -((2 * np.pi * frequency)**2)*amplitude*np.sin(2* np.pi * frequency * x + phase)

# import data
# file_name = "Ramp1.csv"
# file_name = "Ramp_long.csv"
# file_name = "Ramp_long2.csv"
# file_name= 'rampmm.csv'
# file_name = 'reactiontime.csv'
# file_name = 'Step4.csv'
file_name = 'rampcm.csv'
# file_name = '0.7-0.9ramp-1mV-steps-ramp-time(350ms)3.csv'
# file_name = 'C:\Users\jpmet\BAP\BAP\Metingen 22-06-23\0.7-0.9ramp-1mV-steps-ramp-time(350ms)3.csv'
df = pd.read_csv(file_name)
x_data = df['Timestamp']
# x_data = df['']
y_data = df['Data']

# # Use half of data, since it is mirrored
x_data = x_data[0:len(x_data)//2].to_numpy()
y_data = y_data[0:len(y_data)//2].to_numpy()

# x_data = x_data.to_numpy()
# y_data = y_data.to_numpy()
# print(y_data)

# print(time_ax, signal)
# Generate sample data
Fs = 1/1e-3
freq = 50
samples = 500

# Generate noise
mean = 0  # Mean of the noise
std_dev = 0.5  # Standard deviation of the noise
noise = np.random.normal(mean, std_dev, samples)

# sine, x_data = discrete_sine(Fs, freq, samples)
# offset = np.linspace(0,4, num=int(samples))
# y_data = 5*sine + offset + noise
plt.figure()
plt.plot(x_data, y_data)
plt.show()

# make a guess
fft_guess = np.abs(fft.rfft(y_data))
plt.figure()
plt.stem(fft_guess)
plt.show()
# Remove DC component
index = np.where(fft_guess[1:] == np.max(fft_guess[1:]))[0]

fft_freq = fft.rfftfreq(len(y_data), 1/Fs)
print("Frequency", index[0], fft_freq[index])
# [amp,freq,phase,offset]
freq_init = fft_freq[index]
print(freq_init)#freq_init[0]
initial_guess = [0.1,0.1 ,0, 0, 0.01]

# Perform the least squares fit using curve_fit
optimized_params, _ = curve_fit(sine_func, x_data, y_data, p0=initial_guess, maxfev=int(10000))

# Extract the optimized parameters
amplitude_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt = optimized_params
print(optimized_params)

fig = plt.figure()
plt.scatter(x_data, second_derivative(x_data,amplitude_opt,frequency_opt, phase_opt), marker='.')
plt.xlabel("Time [s]")
plt.ylabel("DC-output Interferometer [V]")
plt.show()
image_name = "sine_fit_derivative.svg"
image_format = "svg"
fig.savefig(image_name, format=image_format, dpi=1200)

second_derivative_fitted = second_derivative(x_data,amplitude_opt,frequency_opt, phase_opt)
error = 0.0001
print(type(second_derivative_fitted), second_derivative_fitted)
zero_indices = np.where(np.abs(second_derivative_fitted)<error)[0]
print("zero_indices", zero_indices)
roots = fsolve(second_derivative, x_data[zero_indices], args=(amplitude_opt, frequency_opt, phase_opt))
roots = np.unique(np.around(roots, decimals=6))
derivs = first_derivative(roots, amplitude_opt, frequency_opt, phase_opt, offset_slope_opt)
print("roots", roots, np.sign(derivs))
quad_points = sine_func(roots, amplitude_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt)
# Plot the original data and the fitted curve
fig = plt.figure()

plt.scatter(x_data, y_data, label='Original Data', marker='o', color='red')
plt.plot(x_data, sine_func(x_data, amplitude_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt),color='blue', label='Fitted Curve')
plt.scatter(roots, quad_points, color='blue', marker='x')
plt.xlabel("Time [s]")
plt.ylabel("DC-output Interferometer [V]")
plt.legend()
plt.grid()
plt.show()
image_name = "sine_fit.svg"
image_format = "svg"
fig.savefig(image_name, format=image_format, dpi=1200)
