""" Data Processing """
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from random_plant import *


#------------ Generate data ------------#
F = 10                              # Hz
SAMPLE_RATE = 100_000               # 1kHz sample rate
DURATION = 5                        # 10 seconds
N_SAMPLES = DURATION*SAMPLE_RATE    # Number of samples
# t = np.arange(DURATION,step=DURATION/N_SAMPLES)

data_in, t_out, data_out = generate_data(F, SAMPLE_RATE, DURATION)

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
#------------ Define model ------------#
linear_model = LinearRegression()

#------------ Train model ------------#
linear_model.fit(x, y)
score = linear_model.score(x, y)

print(score)
print(linear_model.coef_)

# plt.figure()
# plt.plot(t,filt, color='r')
# plt.plot(t, signal_t, color= 'b')

# plt.figure()
# plt.stem(fft_out_x[:], fft_out_psd[:], 'x')
# plt.show()
