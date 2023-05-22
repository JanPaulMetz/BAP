"""Log scale linear trasnfer"""
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal, fft
from transfer_calculation import *
from calculate_fft import *
import sys
"""
# Sweep frequency
START = 0
STOP = 1_500_000
SAMPLE_RATE = 1_100_000
N_SWEEPS = 100
DURATION = 0.0009
N_SAMPLES = int(DURATION*SAMPLE_RATE)
data_in, data_out, time_axis = frequency_sweep(START,STOP,SAMPLE_RATE,DURATION, N_SWEEPS)
"""

get_transfer_power()
sys.exit()
def get_bin_size(frequency, periods_per_bin, sample_rate):
    """Get sample size based on input frequency and required periods per sample"""
    period_t = 1/frequency
    bin_n = period_t*sample_rate*periods_per_bin
    # for periods_per_bin in range(1, max_periods_per_bin):
    #     bin_n = period_t*sample_rate*periods_per_bin
    #     print(bin_n)
    #     print(bin_n.is_integer())
    #     if bin_n.is_integer(): # if integer
    #         break
    #     # else continue increasing periods
    return bin_n

def get_duration(bin_size, sample_rate):
    """Get duration bassed on sample_size and sample_rate"""
    duration = bin_size/sample_rate
    return duration

#TODO: Improve run time 
def scale_axis(axis, new_bin_size):
    """Scale omega axis to desired bin size"""
    original_size = axis.size
    bin_ratio = new_bin_size / original_size

    axis_scaled = np.zeros(new_bin_size)
    for i in range(original_size):
        axis_scaled[int(i*bin_ratio)] = axis[i]
    return axis_scaled

"""DEV choose binsize and correct for different samplesizes"""

START = 20e3
STOP = 1.3e6
SAMPLE_RATE = 65e6 # Msample/s
PERIODS_PER_BIN = 10 # periods per sample
N_SWEEPS = 10

# data_in, time_axis, data_out = generate_data(1_500_000, SAMPLE_RATE, 0.000004)
# calculate_signal_fft(time_axis,data_in,SAMPLE_RATE)

# Maximum sample size if duratio is maximum so at lowest frequency
max_bin_size = get_bin_size(START, PERIODS_PER_BIN, SAMPLE_RATE)
max_bin_size = np.ceil(max_bin_size)
print("max_bin_size", max_bin_size)

# Get array containing bin sizes
log_space = get_log_space(START, STOP, N_SWEEPS) #get_bin_size(frequency, PERIODS_PER_BIN, SAMPLE_RATE)

duration = get_duration(max_bin_size,SAMPLE_RATE)
# data_in, time_axis, data_out = generate_data(freq, SAMPLE_RATE, duration)

data_in_fft = np.zeros((N_SWEEPS, int(max_bin_size)))
data_out_fft = np.zeros((N_SWEEPS, int(max_bin_size)))
# Calculate fft and then magnitude and frequency response



bin_size = get_bin_size(START, PERIODS_PER_BIN, SAMPLE_RATE)
duration = get_duration(bin_size, SAMPLE_RATE)
data_in, time_axis, data_out = generate_data(START, SAMPLE_RATE, duration)
omega_init, fft_init = calculate_signal_fft(time_axis, data_in, SAMPLE_RATE)
max_bin_size = omega_init.size

omega_in_scaled = np.empty((N_SWEEPS, int(max_bin_size)))
fft_in_scaled = np.empty((N_SWEEPS, int(max_bin_size)))
for i, frequency in enumerate(log_space):
    # Get bin size and duration
    bin_size = get_bin_size(frequency, PERIODS_PER_BIN, SAMPLE_RATE)
    duration = get_duration(bin_size, SAMPLE_RATE)

    # get time data
    data_in, time_axis, data_out = generate_data(frequency, SAMPLE_RATE, duration)
    print("time ax",time_axis.shape)
    
    # get fft
    omega_in, fft_in = calculate_signal_fft(time_axis, data_in, SAMPLE_RATE)

    fft_in_scaled[i,:] = scale_axis(np.abs(fft_in), max_bin_size)
    # ax[i].set_label(frequency)
    # ax[i].stem(omega_init[:], fft_scaled[:], label=frequency)
    # ax[i].legend()

    # sys.exit()
    # data_out_fft[i, :] = calculate_signal_fft(
    #     time_axis, data_out[i, :], SAMPLE_RATE)[1]
    
    # magnitude_response[i, :] = calculate_transfer_magnitude(
    #     data_in_fft[i, :], data_out_fft[i, :])
    # phase_response[i, :] = calculate_transfer_phase(
    #     data_in_fft[i, :], data_out_fft[i, :])





"""END DEV bin size&compensation"""

""" DEV HANN"""
# # Create Hann window
# hann_window = signal.windows.hann(N_SAMPLES)
# plt.figure()
# plt.plot(time_axis, data_in[50,:])
# plt.show()
# data_in[20] = d
""" END DEV"""
f_cutoff = 500_000
num, den = signal.butter(1, [f_cutoff], analog=False,btype='lowpass', fs=SAMPLE_RATE)

mag_resp, ind_mag, phase_resp, ind_phase = get_transfer(time_axis, data_in, data_out, SAMPLE_RATE, DURATION)#STOP,
w,h = signal.freqz(num, den)
w_log = np.logspace(1,np.log10(SAMPLE_RATE/2), num=512)# np.linspace(0, SAMPLE_RATE/2, num=512)
w_log = np.logspace(1,np.log10(STOP), num=512)
w_lin = np.linspace(0,SAMPLE_RATE/2, num=512)
fit = np.polyfit(ind_mag,mag_resp, deg=3)
mag_fit = np.polyval(fit, w_log)
print("weights: ", fit)

fit = np.polyfit(ind_phase, phase_resp, deg=2)
phase_fit = np.polyval(fit, w_log)
figure, ax = plt.subplots(2,1)


# Plot magnitude response
ax[0].scatter(ind_mag, (20*np.log10(np.abs(mag_resp))), marker='.',color='r',label='Calculated Response')
# ax[0].scatter(w_log, (20*np.log10(np.abs(mag_fit))), color='y',marker='.', label='Fit')
ax[0].semilogx(w_lin,  20*np.log10(np.abs(h)), ls='dashed', label='Simulated Response')
# Plot phase response
ax[1].scatter(ind_phase,np.rad2deg(phase_resp), color='red',marker='.', label='Calculated Response')
# ax[1].plot(w_log,np.rad2deg(phase_fit), color='y',marker='.', label='Fit')
ax[1].semilogx(w_lin, np.rad2deg(np.unwrap(np.angle(h))), ls='dashed', label='Simulated Response')
# Plot lines at -3dB 
ax[0].axvline(f_cutoff, ls='dashed', color='green')
ax[0].axhline(-3, ls='dashed', color='green')
# Plot grid
ax[0].grid(which='both', axis='both')
ax[1].grid(which='both', axis='both')
# Set labels 
plt.setp(ax[0], xlabel="Frequency (Hz)",ylabel="Magnitude (dB)")
plt.setp(ax[1], xlabel="Frequency (Hz)",ylabel="Phase (degrees)")
# Plot Legend
ax[1].legend()
ax[0].legend()
plt.show()