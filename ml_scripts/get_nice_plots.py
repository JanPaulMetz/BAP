""" Use this to make plots for reporting """
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys

from calculate_fft import *
from generate_data import generate_data, generate_discrete_sine
from transfer_calculation import *


from scipy.fft import rfft, rfftfreq
# bin_size = 
sample_rate=1e5#65e6

x_axis,sine = generate_discrete_sine(1e4, sample_rate, 0.03)
hann_window = np.copy(signal.windows.hann(int(len(sine)), False))
# fig,ax = plt.subplots(2)
# ax[0].plot(x_axis, sine, label='Sine wave')
# ax[0].plot(x_axis, hann_window, color='red', label='Hann window')
# ax[1].plot(x_axis, hann_window*sine, label='Windowed sine wave')
# ax[0].legend(loc='upper right')
# ax[0].set_ylabel('Amplitude')
# ax[1].set_ylabel('Amplitude')
# ax[1].set_xlabel('Time (seconds)')
# ax[1].legend()
# plt.show()
windowed = sine*hann_window
fft_size = len(fft(hann_window))
fft_sine = 1.63*rfft(windowed)/fft_size
fft_window = fft(hann_window)/fft_size
fft_bad = rfft(sine)/fft_size
omega = fftfreq(hann_window.size, 1/sample_rate)

plt.figure()
plt.stem(omega, 20*np.log10(np.max(np.abs(fft_window))))
# plt.xlim([0,1.3475e6])
plt.show()
sys.exit()
fig, ax = plt.subplots(2)

ax[0].stem(omega,np.abs(fft_bad), label='Sinewave')
ax[1].stem(omega,np.abs(fft_sine), label='Windowed sinewave')
ax[0].set_xlim([1.3375e6,1.3475e6])
ax[1].set_xlim([1.3375e6,1.3475e6])
ax[0].set_ylabel('Amplitude')
ax[1].set_ylabel('Amplitude')
ax[1].set_xlabel('Frequency (Hz)')
ax[0].legend()
ax[1].legend()
plt.show()
max_index = np.where(np.abs(fft_bad) == np.max(np.abs(fft_bad)))[0]
print(max_index)
fig, ax = plt.subplots(2)

ax[0].stem(omega,np.abs(fft_bad), label='Sinewave')
ax[0].stem(omega[int(max_index-1):int(max_index+3)],np.abs(fft_bad[int(max_index-1):int(max_index+3)]), markerfmt='red', linefmt='red')
ax[1].stem(omega,np.abs(fft_sine), label='Windowed sinewave')
ax[1].stem(omega[int(max_index-1):int(max_index+3)],np.abs(fft_sine[int(max_index-1):int(max_index+3)]), markerfmt='red',linefmt='red')
ax[0].set_xlim([1.3375e6,1.3475e6])
ax[1].set_xlim([1.3375e6,1.3475e6])
ax[0].set_ylabel('Amplitude')
ax[1].set_ylabel('Amplitude')
ax[1].set_xlabel('Frequency (Hz)')
ax[0].legend()
ax[1].legend()
# plt.stem(omega, np.abs(fft_bad))

plt.show()

sys.exit()
""" GET PHASE AND MAGNITUDE """
# Helper functions: 
def get_max_index(input_array):
    """Get max index of input array"""
    return np.where(input_array == np.max(input_array))[0]
# system constants:
start = 1.58e5
stop = 1.68e7
sample_rate = 65e6
periods_per_bin = 100
n_sweeps = 100

# size around max peak collected
power_bin_size = 2

# bin size and duration:
bin_size = periods_per_bin*sample_rate/start
duration = periods_per_bin/start

# Define arrays
data_in = np.zeros((n_sweeps, int(bin_size)))
data_out = np.zeros((n_sweeps, int(bin_size)))

# sweep frequency
data_in, data_out, time_axis = frequency_sweep(start, stop, sample_rate, duration, n_sweeps)

# Define window
hann_window = np.copy(signal.windows.hann(int(bin_size), False))
print(hann_window.size)

# Degine fft arrays
window_in_fft = np.zeros((n_sweeps, int(bin_size//2)), dtype="complex_")
fft_size = int(rfft(data_in[0,:]).size)
in_fft = np.zeros((n_sweeps, fft_size), dtype="complex_")
out_fft = np.zeros((n_sweeps, fft_size), dtype="complex_")
freq_logspace = get_log_space(start, stop, n_sweeps)
transfer_magnitude = np.zeros(n_sweeps)
phase_arc = np.zeros(n_sweeps)
phase = np.zeros(n_sweeps)
for i, frequency in enumerate(freq_logspace):
# Multiply data with window
    window_in = hann_window*data_in[i,:]
    window_out = hann_window*data_out[i,:]
    # print("Shape window",window_in.shape)

# FFT of windowed signal 1.63 window compensation
    in_fft[i,:] = 1.63*rfft(window_in)/fft_size
    out_fft[i,:] = 1.63*rfft(window_out)/fft_size
    omega = rfftfreq(window_in.size, 1/sample_rate)

# Get max index
    max_index_in = get_max_index(np.abs(in_fft[i,:]))
    max_index_out = get_max_index(np.abs(out_fft[i,:]))
    # print("max index",max_index_in)

# Capture all power around max index (p=s(t)^2)
    upper_index_in = int(max_index_in + power_bin_size)
    lower_index_in = int(max_index_in - power_bin_size)

    upper_index_out = int(max_index_out + power_bin_size)
    lower_index_out = int(max_index_out - power_bin_size)

    values_around_peak_in = np.abs(in_fft[i, lower_index_in:upper_index_in])
    values_around_peak_out = np.abs(out_fft[i, lower_index_out:upper_index_out])

# Get transfer function
    transfer = out_fft[i,max_index_in]/in_fft[i,max_index_in]

# /_H(s) = arctan(im(H)/re(H))
    phase_arc[i] = np.arctan(np.imag(transfer)/np.real(transfer))
    phase[i] = np.angle(transfer)
    print(phase_arc[i], phase[i])

# Power P = |X(f)|^2
    power_in = np.sum((values_around_peak_in)**2)
    power_out = np.sum((values_around_peak_out)**2)

    print("freq", frequency)
    print("power_in windowed", power_in)
    print("power_out windowed", power_out)

# |H| = power_out/power_in
    transfer_magnitude[i] = power_out/power_in

n_plots = 2
f_cutoff = 1.67e6
num, den = signal.butter(1, [f_cutoff], analog=False,btype='lowpass', fs=sample_rate)
w,h = signal.freqz(num, den)
w_lin = np.linspace(0,sample_rate/2, num=512)

y_max = 1
y_min = -10
plt.figure()
plt.semilogx(w_lin,  20*np.log10(np.abs(h)), ls='dashed', label='Simulated Response')
plt.scatter(freq_logspace, 10*np.log10(transfer_magnitude), marker=".", color='red', label='Result')
plt.vlines(f_cutoff,ymin=y_min, ymax=y_max, ls='dashed', color='green',label="-3dB frequency")
plt.hlines(-3,xmin=start, xmax=stop, ls='dashed', color='green')
plt.xlim([start,f_cutoff + 2e6])
plt.ylim([-4, 0])
plt.ylabel("Magnitude response (dB)")
plt.xlabel("Frequency (Hz)")
plt.grid()
# plt.xticks(np.linspace(start,stop, num=10))
plt.legend()
plt.show()

plt.figure()
plt.scatter(freq_logspace, (phase), marker='.', color='red', label="Result")
plt.semilogx(w_lin,  (np.unwrap(np.angle(h))), ls='dashed', label='Simulated Response')
plt.ylabel("Phase response (Radians)")
plt.xlabel("Frequency (Hz)")
plt.xlim([start,f_cutoff + 2e6])
plt.ylim(np.min(phase),np.max(phase))
plt.grid()
plt.legend()
plt.show()
""" """
