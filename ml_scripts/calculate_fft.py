"""Module for fft calculations"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq

def calculate_signal_fft(x_signal, y_discrete, sample_rate):
    """Calculate discrete signal fourier transform"""
    u_fft = fft(y_discrete)[0:x_signal.size//2]
    omega = fftfreq(x_signal.size, 1/sample_rate)[0:x_signal.size//2]
    # fig, ax = plt.subplots(2)
    # ax[0].stem(omega,np.abs(u_fft/x_signal.size)) #x_signal.size
    # ax[1].plot(x_signal, y_discrete)
    # plt.show()
    return omega, u_fft/(u_fft.size)#/(x_signal.size//2)

def fft_to_singlesided(omega, fft_in, sample_rate, duration):
    """Convert double sided fft to signlesided"""
    fft_singlesided = np.empty((fft_in.shape))
    omega_singlesided = np.empty((omega.shape))
    index_mid = int(sample_rate*duration/2)
    #index_end = int(sample_rate*duration)
    omega_singlesided = np.copy([omega[0:index_mid]])
    fft_singlesided = np.copy([fft_in[0:index_mid]])

    return omega_singlesided[0,:], fft_singlesided

