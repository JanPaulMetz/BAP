""" 90% power located in n samples, against fft size """
import sys
import numpy as np
from numpy.random import default_rng
from scipy.signal import windows
from scipy import fft
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import BoundaryNorm, ListedColormap

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

def number_of_samples(freq, fft, fft_size_local):
    "" "Get number of samples that contains 90% power""" 
    power = 0
    index = get_fft_index(freq, sample_rate, fft_size_local)
    n_samples = 0
    samples = -1
    totpower = np.sum(np.abs(fft)**2)
    print("SIZE", fft_size_local,"Freq", freq,"Totpower", totpower)
    if totpower >1.1:
        plt.figure()
        plt.stem(np.abs(fft))
        # plt.vlines([index,lower_i, upper_i], ymin=0, ymax=1, colors='red')
        plt.show()
    else:
        while power<0.99*totpower:
            # Calculate signal power 
            # print("index",index)
            samples +=1
            upper_i = int(index + samples)
            lower_i = int(index - samples)
            # print("Power samples", n_power_samples[i])
            magnitudes_around_peak = np.abs(fft[lower_i:upper_i])
            # print("mags around peak",len(magnitudes_around_peak))
            power = np.sum(magnitudes_around_peak**2)
            # print("power out",power_out)
            n_samples += 2
        
        # print("old",n_samples, (2*samples)+1)

    # plt.figure()
    # plt.stem(np.abs(fft))
    # plt.vlines([index,lower_i, upper_i], ymin=0, ymax=1, colors='red')
    # plt.show()
    return (2*samples)+1, 100*((2*samples)+1)/fft_size_local

def model():
    x = np.linspace(0,100,num=100)
    y = np.linspace(0,100,num=100)
    # y = 100*np.random.randint(0,1,size=100)
    rng = default_rng()
    # y = rng.standard_normal(100)
    
    x = x[:,np.newaxis]
    y = y[:,np.newaxis]
    print(x.shape, y.shape)
    z = np.dot(x,y.T)
    return x,y,z

# x,y,z= model()
# # z = z[:,:,0]
# print(z.shape, z)
# X,Y = np.meshgrid(x,y)
# fig = plt.figure()

# im = plt.imshow(z, cmap='jet', origin='lower', aspect='auto')#,extent=[x[:,0], x[-1], y[0], y[-1] ])
# cbar = fig.colorbar(im)
# plt.xlabel('freq')
# plt.ylabel('binsize')

# # Show the plot
# plt.show()

# sys.exit()

# System constants
sample_rate = 65e6
center_frequency = 1.59867e6
bandwidth = (1.550e6, 1.65e6)

# fft_size_array = np.linspace(0.75e3, 10e5, num=10)
# pwr = np.linspace(9,16, num=)
# fft_size_array = np.linspace(30e3, 100e3, num=500)
frequencies = np.linspace(1.575e6, 1.625e6, num=30)
# Generate signal
f1 = center_frequency

pwr = np.linspace(8,17, num=10)
print(pwr)
fft_size_array = 2**pwr
fft_size_array = np.linspace(2**8, 2**17, 10)
tick_labels = [f'$2^{{{int(i)}}}$' for i in pwr]
# f2 = 1.57e6
# f3 = 1.632e6
fft_signal = []
# samples_around_peak = np.zeros((fft_size_array.size,frequencies.size))
# percentage = np.zeros((fft_size_array.size,frequencies.size))
samples_around_peak = np.zeros((fft_size_array.size))
percentage = np.zeros((fft_size_array.size))
print(samples_around_peak.shape)
frequency = 1.6e6
for i, fft_size in enumerate(fft_size_array):
    # for j,frequency in enumerate(frequencies):
        # print(i,j)
        # print("freq", frequency, "size", fft_size)
        # Make sure it is int
        fft_size = int(fft_size)

        # Get time signal
        time_signal = discrete_sine(sample_rate, frequency, fft_size)

        

        # time_signal = discrete_sine(sample_rate, center_frequency, fft_size)
        # Window signal
        window_signal = windows.hann(fft_size)
        time_windowed = time_signal#time_signal*window_signal
        print("sizes", fft_size, time_windowed.shape, window_signal.shape)
        # plt.figure()
        # plt.plot(time_signal)
        # plt.plot(window_signal, color='red')
        # plt.show()
        # Get fft
        size = fft_size//2
        fft_signal = fft.rfft(time_windowed)/size#1.63*fft.rfft(time_windowed)/size
        omega_fft = fft.rfftfreq(time_windowed.size, 1/sample_rate)

        # Get number of samples around peak
        samples_around_peak[i], percentage[i] = (number_of_samples(frequency, fft_signal, fft_size))
 
plt.figure()
plt.scatter(fft_size_array, percentage)
plt.scatter(fft_size_array, samples_around_peak, color='red')
plt.show()
# Create a 3D scatter plot
X,Y = np.meshgrid(fft_size_array,frequencies)
# Z = np.reshape(samples_around_peak, (, ))
# fig, ax =  plt.subplots()
# ax = fig.add_subplot(111, projection='3d')
fig = plt.figure()

# Define the levels and colors for the discrete color bar
levels = [0,1,2,3,4,5,6,7,8,9,10,11,12]
# colors = ['blue', 'red','blue', 'red','blue', 'red', 'blue', 'red', 'blue', 'red']

# Create a discrete color map
# cmap = ListedColormap(colors)

# Create a boundary norm to map levels to colors
# norm = BoundaryNorm(levels, len(colors))



print("TEST", samples_around_peak[-1,-1])

im = plt.imshow(samples_around_peak, cmap='jet',origin='lower', aspect='auto',extent=[frequencies[0], frequencies[-1], fft_size_array[0], fft_size_array[-1] ])
# Update the color bar
cbar = fig.colorbar(im, cmap='jet')#,boundaries=levels)#, norm=norm, boundaries=levels, ticks=levels)
# Calculate the powers of 2 for the tick positions
# Generate equally spaced y-tick positions coupled to fft_size_array
ytick_positions = np.linspace(fft_size_array[0], fft_size_array[-1], 10)
plt.rcParams['text.usetex'] = True
# Set the y-tick positions
plt.yticks(ytick_positions)

plt.yticks(ytick_positions,tick_labels)
plt.xlabel('Frequency [Hz]')
plt.ylabel('FFT size [samples]')
plt.title("Number of Samples Required to Capture 90 percent of Power")
image_format = 'svg' # e.g .png, .svg, etc.
image_name = 'fftsize_freq.svg'

fig.savefig(image_name, format=image_format, dpi=1200)
# Set labels and title
# ax.set_xlabel('fftsize')
# ax.set_xticks(fft_size_array)
# ax.set_yticks(frequencies)
# ax.set_ylabel('freqs')
# ax.set_zlabel('samples 90% power')
# ax.set_title('Jpeipeo')

# Show the plot
plt.show()