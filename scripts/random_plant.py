"""Module to implement generating mock data"""
import numpy as np

from scipy import signal
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt


def generate_discrete_sine(freq, sample_rate, duration):
    """Generate a discrete sine wave."""
    # x_sine = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    n_samples = duration*sample_rate
    x_sine = np.arange(duration, step=duration/n_samples)
    frequencies = x_sine * freq
    # 2pi because np.sin takes radians
    u_discrete = np.sin((2 * np.pi) * frequencies)
    return x_sine, u_discrete

# returs fft of signal and also returns horizontal axis (omega)

def calculate_signal_fft(x_signal, y_discrete, sample_rate):
    """Calculate discrete signal fourier transform"""
    u_fft = fft(y_discrete)
    omega = fftfreq(x_signal.size, 1/sample_rate)

    return omega, u_fft/(x_signal.size)

# TO DO: randomize this transferfunction generation
def generate_discrete_tf(sample_rate):
    """Generate a discrete transferfunction."""
    f_cutoff = 20_000
    w = f_cutoff / (sample_rate / 2)
    num, den = signal.butter(1, [f_cutoff], btype='lowpass', analog=False, fs=sample_rate)
    
    # # PRINT 
    # plt.figure()
    # w, h = signal.freqs(num, den) #np.unwrap
    # plt.semilogx(w, 20 * (np.angle(h)), ls='dashed')
    # plt.title('Bessel filter magnitude response (with Butterworth)')
    # plt.xlabel('Frequency [radians / second]')
    # plt.ylabel('Amplitude [dB]')
    # plt.margins(0, 0.1)
    # plt.grid(which='both', axis='both')
    # plt.axvline(100, color='green')  # cutoff frequency
    # plt.show()
    # # b, a = signal.bessel(4, 100, 'low', analog=True, norm='phase')
    # # w, h = signal.freqs(b, a)
    # plt.figure()
    # plt.semilogx(w, 20 * np.log10(np.abs(h)))
    # plt.title('Bessel filter magnitude response (with Butterworth)')
    # plt.xlabel('Frequency [radians / second]')
    # plt.ylabel('Amplitude [dB]')
    # plt.margins(0, 0.1)
    # plt.grid(which='both', axis='both')
    # plt.axvline(100, color='green')  # cutoff frequency
    # plt.show()
    return num, den

def generate_data(frequency, sample_rate, duration):
    """Generate output data by filtering input signal wiht random TF"""
    # Generate transfer-function
    num, den = generate_discrete_tf(sample_rate)
    # Generate discrete sine
    time_axis, signal_t = generate_discrete_sine(
        frequency, sample_rate, duration)
    # Simulate output by filtering time signal with tf
    filt = signal.lfilter(num, den, signal_t)
    return signal_t, time_axis, filt  # MOCK DATA

#  TEST
def test():
    """For testing purposes"""
    time_axis, data = generate_data(10,100_000,5)

    plt.figure()
    plt.plot(time_axis,data, 'r')
    plt.show()

generate_discrete_tf(10_000_000)
# # EXAMPLE:
# import matplotlib.pyplot as plt
# # Set signal properties
# t = np.linspace(0, 100, 500)
# f = 100
# f_s = 1000
# duration = 10

# # Generate TF
# random_TF_discrete = generate_discrete_tf(f_s)

# # Generate sine time
# t, u_t = generate_discrete_sine(f, f_s, duration)

# # Generate sine freq from time (Not needed for simulation)
# omega, u_w = calculate_signal_fft(t,u_t,f_s)

# # Simulate TF with signal u_t. len(t) should be equal to len(u_discrete)
# t_simulate = np.linspace(0,duration, len(u_t))
# sim = signal.dlsim(random_TF_discrete, u_t, t_simulate)

# # Plot
# plt.figure(1)
# plt.plot(sim[0],sim[1])
# plt.show()
