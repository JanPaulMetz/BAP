""" Get map of noisefloor by variating p_min and fft_size"""
import numpy as np
import matplotlib.pyplot as plt

minimum_powers = np.linspace(20, 100, num = 100)/100
# fft_size_array = np.linspace(30.0e3, 40.0e3, num=100)
pwr = np.linspace(0,17, num=18)
print(pwr)
fft_size_array = 2**pwr
print(fft_size_array)
n_samples_90percent_power = 5
bandwidth = 50e3

print((minimum_powers.shape[0], fft_size_array.shape[0]))
# noise_floor = np.zeros((minimum_powers.shape[0],fft_size_array.shape[0]))
# for i, fft_size in enumerate(fft_size_array):
#     for j, minimum_power in enumerate(minimum_powers):
#         print(minimum_power, fft_size)
#         noise_floor[j,i] = 100*fft_size/(n_samples_90percent_power*minimum_power*bandwidth)

noise_floor = np.zeros((minimum_powers.shape[0],fft_size_array.shape[0]))
for j in range(len(fft_size_array)):
    for i in range(len(minimum_powers)):
    
        
        #noise_floor[i,j] = 100*fft_size_array[j]/(n_samples_90percent_power*minimum_powers[i]*bandwidth)
        noise_floor[i,j] = 100*fft_size_array[j]*n_samples_90percent_power*minimum_powers[i]/(bandwidth)
        if 30e3<fft_size_array[j]<31e3:
            print(noise_floor[i,j])


print(noise_floor[0,-1], noise_floor[-1,-1])
print(noise_floor.T.shape)
# X,Y = np.meshgrid(fft_size,minimum_power)
 
fig = plt.figure()

im = plt.imshow(noise_floor.T, cmap='jet', origin='lower', aspect='auto',extent=[minimum_powers[0], minimum_powers[-1],fft_size_array[0],fft_size_array[-1]])
cbar = fig.colorbar(im)
plt.xlabel('Minimum normalized power')
plt.ylabel('FFT size [samples]')
# plt.yticks(fft_size_array)

# plt.xticks(np.linspace(20,100, 10)/100)
# image_format = 'svg' # e.g .png, .svg, etc.
# image_name = 'fftsize_freq.svg'

# fig.savefig(image_name, format=image_format, dpi=1200)


# Show the plot
plt.show()