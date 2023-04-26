from random_plant import *

#------------  Generate data ------------#
t = np.linspace(0,100,500)  # 100 sec
F = 100                     # 100 Hz
SAMPLE_RATE = 1_000         # 1kHz sample rate
DURATION = 10               # 10 seconds

# Generate tf
random_tf_discrete = generate_discrete_tf(SAMPLE_RATE)

# Generate discrete sine
time_axis, signal_t = generate_discrete_sine(F, SAMPLE_RATE, DURATION)

# Simulate tf using signal_t
t_simulate = np.linspace(0,duration, len(signal_t))
