from random_plant import *
import matplotlib.pyplot as plt

#------------ Generate data ------------#
F = 1                   # 100 Hz
SAMPLE_RATE = 1_000         # 1kHz sample rate
DURATION = 1               # 10 seconds
t = np.linspace(0,DURATION,100)  # sec 

# Generate tf
random_tf_discrete = generate_discrete_tf(SAMPLE_RATE)
print("TF : ", random_tf_discrete)
# Generate discrete sine
time_axis, signal_t = generate_discrete_sine(F, SAMPLE_RATE, DURATION)

# Simulate tf using signal_t
t_simulate = np.linspace(0,DURATION, len(signal_t))
t_sim, y_sim = signal.dlsim(system = random_tf_discrete,u = signal_t, t = time_axis)
print("t sim: ", t_sim )
#------------ Preprocess data ------------#
sim_fft = calculate_signal_fft(t_sim, y_sim, SAMPLE_RATE)
print(sim_fft[0][1:100])

# sim_fft = [sim_fft[0][0:int(len(sim_fft[0])/2)], sim_fft[0][-int(len(sim_fft[0])/2):0]]
# plt.figure(1)
# plt.plot(time_axis, signal_t)
# plt.show()

plt.figure(2)
plt.plot(t_sim, y_sim, '+')
plt.xlabel("time")
plt.show()

plt.figure(3)
plt.plot(sim_fft[0], abs(sim_fft[1]), '-')
plt.xlabel("omega")
plt.ylabel("amplitude")
plt.show()
