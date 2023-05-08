""" Data Processing """
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures

from random_plant import *
from calculate_transfer import *
from generate_data import *

#------------ Sweep frequency ------------#
# NOTE: Choose start to stop nicely (even numbers I guess), otherwise problems occur
START = 20
STOP = 80_000
SAMPLE_RATE = 10_000_000
N_SWEEPS = 20
DURATION = 0.001
N_SAMPLES = int(DURATION*SAMPLE_RATE)
data_in, data_out, time_axis = frequency_sweep(START,STOP,SAMPLE_RATE,DURATION, N_SWEEPS)
print("Size data", )
#------------ Get fft of data ------------#

data_in_fft = np.empty((N_SWEEPS,N_SAMPLES))
data_out_fft = np.empty((N_SWEEPS, N_SAMPLES))
data_in_raw = np.empty((N_SWEEPS,N_SAMPLES))
data_out_raw = np.empty((N_SWEEPS,N_SAMPLES))

omega = calculate_signal_fft(time_axis, data_in[0,:], SAMPLE_RATE)[0]

# Sweep N_SWEEPS sines and store in data_in_fft (shape = (N_SWEEPS,N_SAMPLES))
for i in range(N_SWEEPS):
    data_in_fft[i,:] = np.abs(calculate_signal_fft(time_axis, data_in[i,:], SAMPLE_RATE)[1])
    data_out_fft[i,:] = np.abs(calculate_signal_fft(time_axis, data_out[i,:], SAMPLE_RATE)[1])
    # get raw fft for calculating the phase 
    data_in_raw[i,:] = calculate_signal_fft(time_axis, data_in[i,:], SAMPLE_RATE)[1]
    data_out_raw[i,:] = calculate_signal_fft(time_axis, data_out[i,:], SAMPLE_RATE)[1]

# Plot first 4 signals in time and frequency(positive) domain
fig, ax = plt.subplots(4,3, sharex=False, sharey="col")
for i in range(4):
    omega_single_in, single_sided_in = fft_to_singlesided(omega, data_in_fft[i*4,:], SAMPLE_RATE, DURATION)
    omega_single_out, single_sided_out = fft_to_singlesided(omega, data_out_fft[i*4,:], SAMPLE_RATE, DURATION)
    max_index = get_max_index(40, STOP, omega_single_in)
    ax[i,0].stem(omega_single_in[0:max_index],np.abs(single_sided_in[0:max_index]))
    ax[i,1].plot(time_axis, data_in[i*4,:])
    ax[i,2].stem(omega_single_in[0:max_index],np.abs(single_sided_out[0:max_index]))
plt.setp(ax[:,0], xlabel="Frequency (Hz)",ylabel="Magnitude")
plt.setp(ax[0,0], title="Frequency in")
plt.setp(ax[:,1], xlabel="Time (sec)", ylabel="Amplitude")
plt.setp(ax[0,1], title="Time in")
plt.setp(ax[:,2], xlabel="Frequency (Hz)", ylabel="Magnitude")
plt.setp(ax[0,2], title="Frequency out")
plt.show()

#------------ Get magnitude response of sweeped data  ------------#
magnitude_response = np.empty((N_SWEEPS, int(0.5*N_SAMPLES)))
phase_response = np.empty((N_SWEEPS, int(0.5*N_SAMPLES)))
for i in range(N_SWEEPS):
    print("i=", i)
    magnitude_response[i,:] = calculate_transfer_magnitude(data_in_fft[i,:], data_out_fft[i,:])
    phase_response[i,:] = calculate_transfer_phase(data_in_raw[i,:], data_out_raw[i,:])


# Plot magnitude response:
fig, ax = plt.subplots(N_SWEEPS)
for i in range(N_SWEEPS):
    ax[i].stem(omega_single_out[0:max_index],phase_response[i,0:max_index])
plt.show()

# Take total magnitude response by summing seperate magnitude responses:
# magnitude_response_total = np.sum(magnitude_response, axis=0)
# Take the mean of nonzero values:
for i in range(10):
    print("FIrst", magnitude_response[i,0])

magnitude_response_mean, nonzero_ind = mean_transfer(magnitude_response)
phase_response_mean, nonzero_ind_phase = mean_transfer(phase_response)

figure, ax =plt.subplots(2,1, sharex=True)
ax[0].scatter(omega_single_out[0:max_index],magnitude_response_mean[0:max_index])
ax[1].scatter(omega_single_out[0:max_index],phase_response_mean[0:max_index])
plt.show()

plt.figure()
for i in range(N_SWEEPS):
    plt.scatter(omega_single_out[0:max_index],magnitude_response[i,0:max_index])
plt.show()
#------------ Define model ------------#
poly_model = PolynomialFeatures(degree=10)

# #------------ Train model ------------#
magnitude_response_y = magnitude_response_mean[nonzero_ind]

omega_x = omega_single_out[nonzero_ind]

fit = np.polyfit(omega_x,magnitude_response_y, deg=10)
print(np.polyval(fit,omega_x))
plt.figure()
plt.plot(omega_x,np.polyval(fit,omega_x))
plt.scatter(omega_x,magnitude_response_mean[nonzero_ind]) #omega_single_out[nonzero_ind]
plt.show()
magnitude_response_y = magnitude_response_y[np.newaxis,:]
omega_x = omega_x[np.newaxis, :]
poly_model.fit(omega_x, magnitude_response_y)
params = poly_model.transform()
print("Params", params)
# score = poly_model.score(x, y)

# print(score)
# print(poly_model.coef_)

# plt.figure()
# plt.plot(t,filt, color='r')
# plt.plot(t, signal_t, color= 'b')

# plt.figure()
# plt.stem(fft_out_x[:], fft_out_psd[:], 'x')
# plt.show()
