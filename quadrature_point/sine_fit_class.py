""" Class fitting a sine"""
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit, fsolve
from scipy import fft
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import CubicSpline
from scipy.signal import windows, find_peaks

class SineFitter:

    def __init__(self,x_data, y_data, sample_rate):
        self.x_data = x_data
        self.y_data = y_data

    def standardise(self):
        # Normalize data (z-score)
        self.y_data = ((self.y_data - np.mean(self.y_data))/np.std(self.y_data))

    def sine_prototype(self, x, amplitude_offset, amplitude_slope, frequency, phase, offset, offset_slope):
        """ prototype function including amplitude varying with x and offset varying with x
        y(x) = (A + Bx)sin(2pifx + phi) + C + Dx
        x:              x-axis data point(s)
        other inputs:   optimisation parameters
        returns y
        """

        return (amplitude_offset + amplitude_slope * x) * np.sin(2 * np.pi * frequency * x + phase) + offset + offset_slope * x
    
    def get_intial_slope_and_offset(self):
        """ Get initial slope and offset (guesses) by fitting a line with slope and offset"""

        def line_prototype(x, slope, offset):
            """ y(x) = A + Bx"""
            return offset + slope*x
        
        max_iters = 1e4
        initial_guess = [0,0]
        optimised_params, _ = curve_fit(line_prototype, self.x_data, self.y_data, p0=initial_guess, maxfev=int(max_iters))
        slope_opt, offset_opt = optimised_params

        return slope_opt, offset_opt
    
    #TODO: Estimate the ampitude by getting it from 1 period (period is estimated by frequency and sample rate)
    def get_initial_amplitude(self):
        """ Get guess of amplitude"""
        return (np.max(self.y_data) - np.min(self.y_data))/2
    
    #TODO: Estimate the amount of periods present in the sample based on frequency 
    def get_initial_frequency(self):
        """ Get intial frequency by zero-padding the data (increasing frequency resolution) and performing a FFT """
        # Data length after padding
        padded_length = int(1e7)#int(len(self.x_data))

        # zero padding
        y_data_padded = np.pad(self.y_data, (0, padded_length - len(self.y_data)), mode='constant')
        x_data_padded = np.linspace(self.x_data[0], self.x_data[len(self.x_data)-1], num = len(y_data_padded))
        # plt.figure()
        # plt.plot(y_data_padded)
        # plt.show()

        # Outlier detection 
        # percentile = 95  # Adjust the percentile as needed
        # threshold = np.percentile(self.y_data, percentile)
        # non_outliers = np.where(self.y_data < threshold)[0]

        # x_data_new = self.x_data[non_outliers]
        # y_data_new = self.y_data[non_outliers]

        # Interpolation
        x_interpolate = np.linspace(self.x_data[0], self.x_data[len(x_data)-1], num = int(1e4))
        interpolation = CubicSpline(self.x_data, self.y_data)
        y_interpolated = interpolation(x_interpolate)
        y_interpolated = y_interpolated - np.mean(y_interpolated)

        # x_interpolate = np.linspace(x_data_new[0], x_data_new[len(x_data)-1], num = int(400))
        # interpolation = CubicSpline(x_data_new, y_data_new)
        # y_interpolated = interpolation(x_interpolate)

        # window
        window = windows.hann(len(self.y_data))
        # window = windows.hann(len(y_data_padded))
        # window = windows.hann(len(y_interpolated))
        # window = 1
        
        # Calculate magnitudes by FFT
        y_data_f = np.abs(fft.rfft(self.y_data*window))
        # y_data_f = np.abs(fft.rfft(self.y_data))
        # y_data_f = np.abs(fft.rfft(y_interpolated*window))

        # Calculate frequency axis
        samples_per_x = len(self.x_data) / (np.max(self.x_data) - np.min(self.x_data))
        # samples_per_x = len(x_interpolate) / (np.max(x_interpolate) - np.min(x_interpolate))
        # freq_axis = fft.rfftfreq(len(y_interpolated), 1/samples_per_x)
        
        freq_axis = fft.rfftfreq(len(self.y_data), 1/samples_per_x)
        # freq_axis = fft.rfftfreq(len(y_interpolated), 1/samples_per_x)
        print("LENS", len(y_data_f),len(freq_axis) )
        # Get index where frequency power is maximum 
        
        index = np.where(y_data_f == np.max(y_data_f))[0]
        print("MAx", index )

        # Find peaks in the spectrum (only keep the peaks with highest prominence)
        percentile = np.percentile(np.abs(y_data_f), 90)
        print("Percentile", percentile)
        first_peak = freq_axis[index]
        #TODO: Put first peak in the array of peaks!
        peaks_found, _ = find_peaks(np.abs(y_data_f),prominence=([percentile], None))
        peaks = np.concatenate(first_peak, peaks_found)
        print("PEAKS", peaks)

        plt.figure()
        plt.scatter(freq_axis[peaks],y_data_f[peaks] , color='red')
        plt.stem(freq_axis,y_data_f, markerfmt= '.')
        
        # plt.stem(freq_axis,y_data_f)
        plt.show()
        # Get the frequency at index
        first_peak = peaks[0]
        
        # Get center of weight of peaks
        centers_of_weight = np.zeros(len(peaks))
        for i, peak in enumerate(peaks):
            total_weight = y_data_f[peak-1] + y_data_f[peak] + y_data_f[peak+1]
            freq_weight_contribution = freq_axis[peak-1]*y_data_f[peak-1] + freq_axis[peak]*y_data_f[peak] + freq_axis[peak+1]*y_data_f[peak+1]
            center_of_weight = freq_weight_contribution/total_weight
            print(center_of_weight)
            centers_of_weight[i] = center_of_weight
        # print("ratio", ratio,int(first_peak*(1-ratio/2)), int(first_peak*(1+ratio/2)))
        # frequency_init = freq_axis[peaks]#freq_axis[index]
        print("freq", centers_of_weight)
        return first_peak, centers_of_weight
    
    def fit(self, plot):
        """ Fittin the prototype on x_data and y_data using initial guesses of parameters """
        # Get initial parameters
        frequency, frequency_peaks = self.get_initial_frequency() #self.get_initial_frequency()
        amplitude_offset = self.get_initial_amplitude()
        amplitude_slope = amplitude_offset
        
        phase = 0
        slope, offset = self.get_intial_slope_and_offset()

        max_freq_iters = len(frequency_peaks)
        mse_threshold = 0.5
        print("PEAKS", frequency_peaks)
        mse_history = []
        frequency_history = []
        parameters_history = []
        previous_mse = 1
        frequency = 0.0088
        for i in range(max_freq_iters):
            # Put in list (used by curve fitter)
            intial_parameters = [amplitude_offset, amplitude_slope, frequency_peaks[i], phase, slope, offset] #frequency_peaks[i]

            # Define max iterations (lower if optimisation takes too long)
            max_iters = 1e7

            # Fit sine on data
            optimised_params, _ = curve_fit(self.sine_prototype, self.x_data, self.y_data, p0=intial_parameters, maxfev=int(max_iters))

            # Unpack parameters
            self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt, self.offset_opt = optimised_params

            # Check if mse is below threshold
            prediction = self.sine_prototype(self.x_data,self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt, self.offset_opt)
            current_mse = np.mean((prediction - self.y_data)**2)

            # Keep track of history
            mse_history.append(current_mse)
            frequency_history.append(frequency_peaks[i])
            parameters_history.append(optimised_params)

            # Break if previous mse was better than current
            print("MSE", current_mse, "f", frequency_peaks[i])
            # if previous_mse < current_mse:
            #     break
            
            # Store current to previous mse
            previous_mse = current_mse

        # Get best mse
        
        best_mse_index = np.where(mse_history == np.min(mse_history))[0]
        print("Best mse", best_mse_index)
        optimised_params = parameters_history[best_mse_index[0]]
        self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt, self.offset_opt = optimised_params
        

        # Make plot of fit and data
        if plot:
             # Get the fitted sine
            x_plot = np.linspace(self.x_data[0], self.x_data[len(self.x_data)-1], 10*len(self.x_data))
            fitted_sine = self.sine_prototype(x_plot, self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt, self.offset_opt)
            figure = plt.figure()
            plt.title("Sine fit")
            plt.scatter(self.x_data,self.y_data, marker="d", label="Original Data")
            plt.plot(x_plot, fitted_sine, color='red', label="Optimized sine")
            plt.xlabel("Wavelength [$nm$]")
            plt.ylabel("Intensity [$\mu W$]")
            plt.legend()
            plt.show()
            # self.save_figure(figure, "sinefit_set2.svg")

        print("Freq opt", self.frequency_opt)

    def get_quad_points(self, plot):
        """ Get quadpoints"""
        # x_ax = np.linspace(0, 5, num = 1000)
        # amplitude_slope = 0.5
        # amplitude_offset = 1
        # frequency = 10
        # phase = 0
        # offset = 0
        # offset_slope = 0.1
        def first_derivative(x, amplitude_offset, amplitude_slope, frequency, phase, offset_slope):
            return (2 * np.pi * frequency)*(amplitude_offset + amplitude_slope*x)*np.cos(2*np.pi*frequency*x + phase) + amplitude_slope * np.sin(2*np.pi*frequency*x + phase) + offset_slope

        def second_derivative(x, amplitude_offset, amplitude_slope, frequency, phase):
            # return -((2*np.pi*frequency)**2)*(amplitude_offset + amplitude_slope*x)*np.sin(2* np.pi * frequency * x + phase) + 4*np.pi*amplitude_slope*np.cos(2*np.pi*frequency*x + phase)
            return amplitude_slope * np.sin(2*np.pi*frequency*x + phase) + 2*np.pi*frequency*amplitude_slope * np.cos(2*np.pi*frequency*x + phase) - (2*np.pi*frequency)**2*(amplitude_offset + amplitude_slope*x) * np.sin(2*np.pi*frequency*x + phase)


        # fig,ax = plt.subplots(3,1)
        # ax[0].plot(x_ax, self.sine_prototype(x_ax,amplitude_offset,amplitude_slope, frequency, phase,offset, offset_slope))
        # ax[1].plot(x_ax, first_derivative(x_ax, amplitude_offset, amplitude_slope, frequency, phase, offset_slope))
        # ax[2].plot(x_ax, second_derivative(x_ax,amplitude_offset, amplitude_slope, frequency, phase))
        # plt.show()
        second_derivative_fitted = second_derivative(self.x_data,self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt)
        error = 0.0001
        zero_crossings_rough = np.where(np.abs(second_derivative_fitted)<error)[0]
        roots = fsolve(second_derivative, x_data[zero_crossings_rough], args=(self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt))
        roots = np.unique(np.around(roots, decimals=6))

        #DEBUG: printing
        print("rough roots", zero_crossings_rough)
        print("ROOTS", roots)
        


        quad_points = self.sine_prototype(roots, self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt, self.offset_opt)
        print("Quad points",quad_points )

        fig,ax = plt.subplots(3,1, sharex=True)
        ax[0].scatter(self.x_data, self.y_data, marker= 'd', color='deepskyblue', label='Original Data')
        ax[0].scatter(roots, quad_points, marker= 'x',color='darkgreen', label='Quadrature Points')
        ax[0].plot(self.x_data, self.sine_prototype(self.x_data,self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt, self.offset_opt), color='red', label="Fitted sine")
        
        ax[1].plot(self.x_data, first_derivative(self.x_data, self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt))
        ax[1].scatter(roots, first_derivative(roots, self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt, self.slope_opt))

        ax[2].plot(self.x_data, second_derivative_fitted)
        ax[2].scatter(roots, second_derivative(roots,self.amplitude_offset_opt, self.amplitude_slope_opt, self.frequency_opt, self.phase_opt))
        ax[2].set_xlabel("Time [s]")
        for i in range(3):
            ax[i].grid()
        plt.show()

    def plot(self):
        plt.figure()
        print("LENS", len(self.x_data), len(self.y_data))
        plt.scatter(self.x_data, self.y_data)
        plt.show()

def open_csv_warner(filename):
    """ Open csv file of format Warner"""
    with open(filename, mode='r') as csv_file:
        # Treat as csv file
        csv_reader = csv.reader(csv_file, delimiter=',')

        # Store each row in a list (list of rows)
        data_list = []
        for row in csv_reader:
            data_list.append(list(map(float,row[0].split())))

    # Store the colum = distance(index 1 to end)
    distance = [row[0] for row in data_list]

    # Store the row = wavelength(index 1 to end)
    wavelength = data_list[0][1:]
    
    # Extract data 
    data = [row[1:] for i, row in enumerate(data_list) if i > 0]
    print("DATA", type(data))
    # Normalize data (z-score)
    # data = ((data - np.mean(data))/np.std(data)).tolist()
    return wavelength, data


if __name__ == "__main__":
    #Import dataset1 and 2
    x_data, y_data_set = open_csv_warner("20210523-113619.txt")
    # print(len(x_data), len(y_data) ,y_data)
    x_data = np.array(x_data)
    for i in range(100):

        y_data = np.array(y_data_set[i])
    
    
        dataset1_fitter = SineFitter(x_data, y_data, 1000)
        
        dataset1_fitter.standardise()
        # dataset1_fitter.plot()
        dataset1_fitter.fit(True)
    sys.exit()
    # Import data
    file_name = 'rampcm.csv'
    # file_name = '0.7-0.9ramp-1mV-steps-ramp-time(350ms).csv'
    # file_name = '0.7-0.9ramp-1mV-steps-ramp-time(350ms)3.csv'
    # file_name = '0.7-0.9ramp-1mV-steps-ramp-time(2850ms).csv'
    df = pd.read_csv(file_name)
    x_data = df['Timestamp']
    y_data = df['Data']
    print(len(x_data))

    x_data = x_data[0:len(x_data)//2].to_numpy()
    y_data = y_data[0:len(y_data)//2].to_numpy()

    start = 0
    x_data = x_data[start:]
    y_data = y_data[start:]

    spline = UnivariateSpline(x_data, y_data, k=2)
    second_derivative = spline.derivative(2)
    x_interpolate = np.linspace(x_data[0], x_data[len(x_data)-1], num = int(400))
    interpolation = CubicSpline(x_data, y_data)
    sample_rate = 1000 # sample per sec (1ms sample period)
    # Create sinefitter
    sinefitter = SineFitter(x_data, y_data, sample_rate)
    # sinefitter = SineFitter(x_interpolate, interpolation(x_interpolate), sample_rate)
    sinefitter.standardise()
    # sinefitter.plot()
    sinefitter.plot()
    sinefitter.fit(True)
    sinefitter.get_quad_points(True)

