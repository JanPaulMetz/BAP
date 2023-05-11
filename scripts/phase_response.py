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

f_cutoff = 10_000
num, den = signal.butter(1, [f_cutoff], analog=False,btype='lowpass', fs=SAMPLE_RATE)

mag_resp, ind_mag, phase_resp, ind_phase = get_transfer(time_axis, data_in, data_out, SAMPLE_RATE, STOP, DURATION)
w,h = signal.freqz(num, den)
w = np.linspace(0, SAMPLE_RATE/2, num=512)
fit = np.polyfit(ind_mag,mag_resp, deg=2)
mag_fit = np.polyval(fit, w)
print("weights: ", fit)

fit = np.polyfit(ind_phase, phase_resp, deg=10)
phase_fit = np.polyval(fit, w)
figure, ax = plt.subplots(2,1)


# Plot magnitude response 
ax[0].semilogx(ind_mag, (20*np.log10(np.abs(mag_resp))), color='r',label='Calculated Response')
ax[0].plot(w, (20*np.log10(np.abs(mag_fit))), color='y',marker='o', label='Fit')
ax[0].semilogx(w,  20*np.log10(np.abs(h)), ls='dashed', label='Simulated Response')
# Plot phase response
ax[1].semilogx(ind_phase,np.rad2deg(phase_resp), color='red', label='Calculated Response')
ax[1].plot(w,np.rad2deg(phase_fit), color='y',marker='o', label='Fit')
ax[1].semilogx(w, np.rad2deg(np.unwrap(np.angle(h))), ls='dashed', label='Simulated Response')
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
