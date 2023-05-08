"""Test phase response and plot"""
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures

from random_plant import *
from calculate_transfer import *
from generate_data import *

#------------ Sweep frequency ------------#
# NOTE: Choose start to stop nicely (even numbers I guess), otherwise problems occur
START = 0
STOP = 80_000
SAMPLE_RATE = 180_000
N_SWEEPS = 20
DURATION = 0.01
N_SAMPLES = int(DURATION*SAMPLE_RATE)
data_in, data_out, time_axis = frequency_sweep(START,STOP,SAMPLE_RATE,DURATION, N_SWEEPS)
# print("Size data", data_in.shape )

data_in_raw = np.empty((N_SWEEPS,N_SAMPLES), dtype='complex_')
data_out_raw = np.empty((N_SWEEPS,N_SAMPLES),dtype='complex_')

omega = calculate_signal_fft(time_axis, data_in[0,:], SAMPLE_RATE)[0]

# Sweep N_SWEEPS sines and store in data_in_fft (shape = (N_SWEEPS,N_SAMPLES))
for i in range(N_SWEEPS):
    # get raw fft for calculating the phase
    data_in_raw[i,:] = calculate_signal_fft(time_axis, data_in[i,:], SAMPLE_RATE)[1]
    data_out_raw[i,:] = calculate_signal_fft(time_axis, data_out[i,:], SAMPLE_RATE)[1]
# print(data_in_raw)
phase_response = np.empty((N_SWEEPS, int(0.5*N_SAMPLES)))
for i in range(N_SWEEPS):
    # print(i)
    phase_response[i,:] = calculate_transfer_phase(data_in_raw[i,:], data_out_raw[i,:])
# print(1)
omega_single_out, single_sided_out = fft_to_singlesided(omega, data_out_raw[0,:], SAMPLE_RATE, DURATION)
# print(2)
max_index = get_max_index(40, STOP, omega_single_out)

# fig, ax = plt.subplots(5)
# for i in range(5):
#     ax[i].stem(omega_single_out[0:max_index],phase_response[i,0:max_index])
# plt.show()

phase_response_mean, nonzero_ind_phase = mean_transfer(phase_response)

phase_response_mean, nonzero_ind_phase = mean_transfer(phase_response)
omega_single_out = omega_single_out[nonzero_ind_phase]

f_cutoff = 20_000
num, den = signal.butter(1, [f_cutoff], btype='lowpass', fs=2*np.pi*SAMPLE_RATE)
w,h = signal.freqz(num, den)
# w = np.linspace(0,DURATION*SAMPLE_RATE/2, num=512)
mag_resp, ind_mag, phase_resp, ind_phase = get_transfer(time_axis, data_in, data_out, SAMPLE_RATE, STOP, DURATION)
# print(mag_resp.size)
fit = np.polyfit(ind_mag,mag_resp, deg=10)

figure, ax = plt.subplots(2,1)
# print("ind", ind_mag)
# x_axis = SAMPLE_RATE *
omega_axis = 10*(0.5 / (np.pi)) * ind_mag
print("indmag", ind_mag)
ax[0].semilogx(omega_axis, (20*np.log10(np.abs(mag_resp))), color='r')
# b, a = signal.butter(1, 0.5, 'low', analog=True)

# w,h = signal.freqz(num, den)
# ax[0].semilogx(w, 20 * np.log10(abs(h)))
ax[1].semilogx(w,  20*np.log10(h), ls='dashed')
ax[0].axvline(f_cutoff, color='green')
ax[0].axhline(-3, color='green')
ax[1].axvline(f_cutoff, color='green')
ax[1].axhline(-3, color='green')
ax[0].grid(which='both', axis='both')
plt.setp(ax[0], xlabel="Frequency (Hz)",ylabel="Magnitude (dB)")
#ax[1].semilogx(ind_phase,phase_resp, color='b')
ax[1].grid(which='both', axis='both')
plt.show()
