"""This module is ment for playing around with radial basis functions"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
from random_plant import nonlinear_system
from calculate_transfer import get_transfer

# Linear function
mag_resp, ind_mag, phase_resp, ind_phase = get_transfer(time_axis, data_in, data_out, SAMPLE_RATE, STOP, DURATION)

# n steps
n = 10
freq = np.logspace(0, 2, n)
power = np.linspace(0, 1, n)
freq, power = np.meshgrid(freq,power)

z = nonlinear_system(freq,power)
print(z.shape)
# Radial basis : 
RBFInterpolator(freq,power,z)

# fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
# ax.plot_surface(freq, power, z, cmap='viridis')
# ax.set_xlabel("freq")
# ax.set_ylabel("power")
# plt.show()
