"""Module for generating test data"""
import numpy as np
from scipy import signal

def generate_discrete_sine(freq, sample_rate, duration):
    """Generate a discrete sine wave."""
    # x_sine = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    n_samples = int(duration*sample_rate)
    x_sine = np.arange(duration, step=duration/n_samples)
    frequencies = x_sine * freq
    # 2pi because np.sin takes radians
    u_discrete = np.sin((2 * np.pi) * frequencies)
    return x_sine, u_discrete

# TODO: randomize this transferfunction generation
def generate_discrete_tf(sample_rate):
    """Generate a discrete transferfunction."""
    f_cutoff = 500_000
    #w = f_cutoff / (sample_rate / 2)
    num, den = signal.butter(1, [f_cutoff], btype='lowpass', analog=False, fs=sample_rate)
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

def nonlinear_system(frequency, power):
    """Generate nonlinear system with power and frequency dependency"""
    f = frequency
    p = power
    w0 = 2.16536024e-10
    w1 = -2.77870690e-05
    w2 = 9.58644453e-01
    weights = np.array([w0, w1, w2, 10000])
    f = np.array([np.ones(f.shape), f, f**2, p**2])
    
    transfer = np.multiply(f.T,weights)
    # Sum all "features" to get data points
    transfer = np.sum(transfer, axis=2)
    # Turn around freq and p to compensate for ^
    transfer = transfer.T
    # transfer_freq = 1*f + 0.05*f**2 + 0.03*f**3
    # transfer_power = 1*p + 0.05*p**2 + 0.03*p**3
    # transfer = transfer_freq + transfer_power
    return transfer#, np.array([f,p])
  