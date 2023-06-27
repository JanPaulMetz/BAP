""" Analysis on noise floor, fft size and output power"""
import numpy as np
from scipy.signal import windows
from scipy import fft
import matplotlib.pyplot as plt

def get_fft_index(frequency, sample_rate, bin_size):
    """ Get index at which this frequency component is placed 
        after performing a DTFT
        bin_size im bits
    """
    # Calculate frequency spacing
    delta_f = sample_rate/bin_size
    # Calculate the bin_number (is the index)
    bin_number = np.divide(frequency,delta_f)
    bin_number = np.round(bin_number)

    return bin_number

def discrete_sine(sample_rate, frequency, num_samples):
    # Create discrete sine 
    time_ax = np.arange(num_samples)/sample_rate
    signal = np.sin(2*np.pi*frequency*time_ax)
    return signal

# System constants
sample_rate = 65e6
center_frequency = 1.59867e6
bandwidth = (1.550e6, 1.65e6)

# fft size
start_pwr = 4
stop_pwr = 18
steps = stop_pwr-start_pwr+1
pwr = np.linspace(8e2, 1e4, num=10)
fft_size_array = pwr
print(pwr, fft_size_array)

# Po min (normalized to 1)
pout = np.linspace(1,10, num=10)
pout_array = pout/10
print(pout)

# Noise floor = Po/(6*numberofsamples) --> Number of samples is function of binsize
fraction = 0.0001
n_power_samples = fraction*fft_size_array//2
print(n_power_samples)

# Generate signal
f1 = center_frequency
f2 = 1.57e6
f3 = 1.632e6
fft_signal = []
for i, fft_size in enumerate(fft_size_array):
    # Make sure it is int
    fft_size = int(fft_size)

    # Get time signal
    time_signal_1 = discrete_sine(sample_rate, center_frequency, fft_size)
    time_signal_2 = 0.5*discrete_sine(sample_rate, f2, fft_size)
    time_signal_3 = 0.25*discrete_sine(sample_rate, f3, fft_size)
    time_signal = time_signal_1 + time_signal_2 + time_signal_3
    # plt.figure()
    # plt.plot(time_signal)
    # plt.show()

    # time_signal = discrete_sine(sample_rate, center_frequency, fft_size)
    # Window signal
    window_signal = windows.hann(fft_size)
    time_windowed = time_signal*window_signal

    # Get fft
    size = fft_size//2
    fft_signal = 1.63*fft.rfft(time_windowed)/size
    omega_fft = fft.rfftfreq(time_windowed.size, 1/sample_rate)

    # Calculate signal power 
    index = get_fft_index(center_frequency, sample_rate, fft_size)
    print("index",index)
    upper_i = int(index + n_power_samples[i]//2)
    lower_i = int(index - n_power_samples[i]//2)
    print("Power samples", n_power_samples[i])
    magnitudes_around_peak = np.abs(fft_signal[lower_i:upper_i])
    print("mags around peak",len(magnitudes_around_peak))
    power_out = np.sum(magnitudes_around_peak**2)
    print("power out",power_out)
    
    # Calculate alowed noise power
    # alowed_noise = power_out/(6*n_power_samples[i])
    # noise = 
    
    print("FFT SIZE",fft_size)
    plt.figure()
    plt.vlines(x= [f1,f2,f3], ymax=1, ymin=0, colors='red')
    plt.stem(omega_fft, np.abs(fft_signal))
    # plt.xlim(bandwidth)
    plt.show()

# Generate noise leve