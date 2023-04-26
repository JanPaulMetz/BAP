# #!/usr/bin/python3
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt

from scipy import signal 
from scipy.fft import fft, ifft, fftfreq

def generate_discrete_sine(freq, sample_rate, duration): 
    x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    frequencies = x * freq
    # 2pi because np.sin takes radians
    u_discrete = np.sin((2 * np.pi) * frequencies)
    
    return x, u_discrete

# returs fft of signal and also returns horizontal axis (omega)
def calculate_signal_fft(x,u_discrete, sample_rate):
    U = fft(u_discrete)
    omega = fftfreq(x.size, 1/sample_rate)

    return omega, U

# TO DO: randomize this transferfunction generation  
def generate_discrete_tf(sample_rate): 
    # Continuous time 
    # num = np.array([1 ,0.5 ,0.5]) 
    # den = np.array([1 ,0.3 ,0.6])
    # Low pass: 
    num = np.array([1])
    den = np.array([1,1])
    random_TF = signal.TransferFunction(num, den)
    # Discrete time 
    random_TF_discrete = random_TF.to_discrete(1/sample_rate)

    return random_TF_discrete


"""" EXAMPLE: 
# Set signal properties
t = np.linspace(0, 100, 500)
f = 100
f_s = 1000
duration = 10

# Generate TF 
random_TF_discrete = generate_discrete_tf(f_s)

# Generate sine cont
t, u_t = generate_discrete_sine(f, f_s, duration)

# Generate sine discrete from cont (Not needed for simulation)
omega, u_w = calculate_signal_fft(t,u_t,f_s)

# Simulate TF with signal u_t. len(t) should be equal to len(u_discrete)
t_simulate = np.linspace(0,duration, len(u_t))
sim = signal.dlsim(random_TF_discrete, u_t, t_simulate)

# Plot 
plt.figure(1)
plt.plot(sim[0],sim[1])
plt.show()
"""