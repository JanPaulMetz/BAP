import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy import fft
import pandas as pd

# file_name = 'Step.csv'
file_name = 'reactiontime.csv'
df = pd.read_csv(file_name)
x_data = df['Timestamp'].to_numpy()
y_data = df['Data'].to_numpy()

y_data = y_data[0:len(y_data)//2]
x_data = x_data[0:len(x_data)//2]
index_low = int(0.75*len(y_data))
index_high = len(y_data)-1
y_final = np.mean(y_data[index_low:index_high])
print(y_final)
y_low = np.min(y_data)
step_start = 0#2000
error = 0.02*y_final
error_up = (y_final + error)
error_low = (y_final - error)

# Extracting rise time (between 0.1 and 0.9 of final value)
rise_level_low = 0.1*(y_final-y_low) + y_low
rise_level_high = 0.9*(y_final-y_low) + y_low

indices_low = [i for i,y in enumerate(y_data) if y < rise_level_low]
print("inds", indices_low, rise_level_low)
# index_low = indices_low.pop()
print("Risetime Index", index_low, x_data[index_low])

indices_high = [i for i, y in enumerate(y_data) if y > rise_level_high]
indices_low = [i for i, y in enumerate(y_data) if y < rise_level_low]
index_high = indices_high[0]
index_low = indices_low[len(indices_low) - 1]
print("HIGH index", index_high, x_data[index_high]-x_data[index_low])
# Settle time
indices = [i for i, y in enumerate(y_data) if error_low < y < error_up and x_data[i] > 2.8]
x_settled = indices[3]
print("Settle time", x_data[x_settled] - x_data[step_start])

fig = plt.figure()
plt.scatter(x_data, y_data, label='Original Data', marker='.')
plt.hlines(y_final, xmin=x_data[step_start], xmax=x_data[x_data.shape[0] -1], color='red', linestyle= "dotted", label="Steady-state")
plt.hlines([error_up, error_low], xmin=x_data[step_start], xmax=x_data[x_data.shape[0] -1], color='red', label=" 2% Error band")
plt.grid()
plt.vlines([x_data[x_settled], x_data[step_start]],  ymin=y_low, ymax=y_final, color='red', linestyle="--", label="Settle-time bounds")
plt.vlines([x_data[index_high], x_data[index_low]],  ymin=y_low, ymax=y_final, color='darkgreen', linestyle="--", label="Rise-time bounds")

plt.ylabel("DC-output Interferometer [V]")
plt.xlabel("Time [s]")
plt.legend()
plt.title("Step response interferometer lambda controller")
plt.show()
