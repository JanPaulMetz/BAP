""" Data Processing """
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures


from random_plant import *
from calculate_transfer import *
from generate_data import *

#------------ Sweep frequency ------------#
START = 50
STOP = 500
SAMPLE_RATE = 100_000
N_SWEEPS = 10
DURATION = 0.1
N_SAMPLES = int(DURATION*SAMPLE_RATE)
data_in, data_out, time_axis = frequency_sweep(START,STOP,SAMPLE_RATE,DURATION, N_SWEEPS)
print("Size data", )
#------------ Get fft of data ------------#

data_in_fft = np.empty((N_SWEEPS,N_SAMPLES))

omega = calculate_signal_fft(time_axis, data_in[0,:], SAMPLE_RATE)[0]

for i in range(N_SWEEPS):
    data_in_fft[i,:] = np.abs(calculate_signal_fft(time_axis, data_in[i,:], SAMPLE_RATE)[1])
    max_index = max_amplitude_index(data_in_fft[i,:])
    print("Max of ", i , max_index, "omega: ", omega[max_index])

fig, ax = plt.subplots(4,2)
for i in range(4):
    ax[i,0].stem(omega,np.abs(data_in_fft[i,:]))
    ax[i,1].plot(time_axis, data_in[i,:])
plt.show()
omega_single, single_sided = fft_to_singlesided(omega, data_in_fft[1,:], SAMPLE_RATE, DURATION)
# print(single_sided)
plt.figure()
plt.stem(omega_single,single_sided)
plt.show()
print("shape fft: ", data_in_fft.shape)

#------------ Preprocess data ------------#
fft_in_x, fft_in_y = calculate_signal_fft(t_out, data_in, SAMPLE_RATE)
fft_out_x, fft_out_y = calculate_signal_fft(t_out, data_out, SAMPLE_RATE) # signal_t
fft_out_psd = np.abs(fft_out_y)/(N_SAMPLES/2) # power spectral density

INDEX_MID = int(SAMPLE_RATE/2)
INDEX_END = int(SAMPLE_RATE)
fft_out_x = np.append(0,[fft_out_x[INDEX_MID:INDEX_END - 1],fft_out_x[0:INDEX_MID - 1]])
fft_out_psd = np.append(0,[fft_out_psd[INDEX_MID:INDEX_END - 1],fft_out_psd[0:INDEX_MID - 1]])

#--- test ----#
fft_in_y = np.array(np.abs(fft_in_y))
fft_out_y = np.array(np.abs(fft_out_y))
x = fft_in_y[:,np.newaxis]
y = fft_out_y[:,np.newaxis]
print(np.shape(x))

#------------ Get features ------------#
magnitude_response = calculate_transfer_magnitude(fft_in_y, fft_out_y)
print("Magniutde response: ", magnitude_response)

# plt.figure()
# plt.stem(magnitude_response)
# plt.show()
#------------ Define model ------------#
# poly_model = PolynomialFeatures(degree=10)

# #------------ Train model ------------#
# PolynomialFeatures.fit(x, y)
# score = poly_model.score(x, y)

# print(score)
# print(poly_model.coef_)

# plt.figure()
# plt.plot(t,filt, color='r')
# plt.plot(t, signal_t, color= 'b')

# plt.figure()
# plt.stem(fft_out_x[:], fft_out_psd[:], 'x')
# plt.show()
