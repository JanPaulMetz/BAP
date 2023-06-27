""" Sine fit on data set"""
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy import fft
from scipy.fftpack import next_fast_len
import sys
from scipy.stats import skew, kurtosis
from scipy.interpolate import CubicSpline

# Return --> fit-score (fit-distance, ) --> plot parameters corresponding score
# Data plot --> dots blue diamond
# open circles voor veel data, fit er overheen met lichte kleur

class SineFit:
    
    def __init__(self, filename, data_set, data_type):
        self.filename = filename
        self.data_set = data_set

        if data_type == 'Warner':
            # Read csv data from text file
            with open(self.filename, mode='r') as csv_file:
                # Treat as csv file
                csv_reader = csv.reader(csv_file, delimiter=',')

                # Store each row in a list (list of rows)
                data_list = []
                for row in csv_reader:
                    data_list.append(list(map(float,row[0].split())))

            # Store the colum = distance(index 1 to end)
            self.distance = [row[0] for row in data_list]

            # Store the row = wavelength(index 1 to end)
            self.wavelength = data_list[0][1:]
            
            # Extract data 
            self.data = [row[1:] for i, row in enumerate(data_list) if i > 0]
            print("DATA", type(self.data))
            # Normalize data (z-score)
            self.data = ((self.data - np.mean(self.data))/np.std(self.data)).tolist()

            
        else:
            df = pd.read_csv(self.filename)
            self.wavelength = df['Timestamp'].to_numpy()
            self.data = df['Data'].to_numpy()  
        
        self.frequency_init_list = []
    
    
    def plot_measurement(self, measurement_number):
        """ Plot 1 measurement, defined by measurement_number"""
        plt.figure()
        plt.title("Measurement {}".format(measurement_number))
        plt.plot(self.wavelength, self.data[measurement_number])
        plt.xlabel("Wavelength [nm?]")
        plt.ylabel("Intensity [V?]")
        plt.show()
    
    def sine_prototype_phase(self,x, amplitude, frequency, phase, offset, offset_slope):
        """ Prototype including offset and slope """
        return amplitude* np.sin(2 * np.pi * frequency * x + phase) + offset + offset_slope*x
    
    def sine_prototype_amplitude_offset(self,x, amplitude, amplitude_offset, frequency, phase, offset, offset_slope):
        """ Prototype including offset and slope """
        # Amplitude --> remove outliers, (max-min)/2
        # Amplitdue offset --> (max-min)/2
        return amplitude*(x)*np.sin(2 * np.pi * frequency * x + phase)  + offset + offset_slope*x + amplitude_offset*np.sin(2 * np.pi * frequency * x + phase)
    
    def get_data(self, measurement_number):
        """ Get data corresponding to measurement number"""
        # Get data from sample number
        y_data = np.array(self.data[measurement_number])
        x_data = np.array(self.wavelength)

        if len(self.wavelength) == len(y_data):
            return x_data, y_data
        else:
            x_data = np.linspace(x_data[0], x_data[len(x_data) - 1], num=len(y_data))
            return x_data, y_data
    
    def set_data(self, measurement_number, new_data):
        """ Set data with new data with different length"""
        print(np.shape(self.data))
        # Resize target to new size
        print(type(self.data))
        self.data[measurement_number] = [0]*len(new_data)
        # Store in the resized list
        self.data[measurement_number][:] = new_data
    
    def slope_and_offset_guess(self,measurement_number, plot):
        """ Get initial guess of slope """
        def y_prototype(x, slope, offset):
            return slope*x + offset
        x_data, y_data = self.get_data(measurement_number)
        max_iters = 1e4
        initial_guess = [0,0]
        optimized_params, _ = curve_fit(y_prototype, x_data, y_data, p0=initial_guess, maxfev=int(max_iters))
        slope_opt, offset_opt = optimized_params
        
        if plot:
            line = y_prototype(x_data,slope_opt, offset_opt)
            plt.figure()
            plt.title("Lin fit of measurement {}".format(measurement_number))
            plt.scatter(x_data,y_data, label="Original Data")
            plt.plot(x_data, line, color='red', label="Optimized sine")
            plt.xlabel("Wavelength [nm]")
            plt.ylabel("Intensity [V]")
            plt.legend()
            plt.show()

        return slope_opt, offset_opt


    def amplitude_guess(self,measurement_number):
        """ Get initial guess of amplitude (max-min)/2 """
        _, y_data = self.get_data(measurement_number)
        return (np.max(y_data) - np.min(y_data))/2
    
    def frequency_guess(self,measurement_number):
        """ Get sample/wavelength of data"""
        # Get data
        x_data, y_data = self.get_data(measurement_number)

    # Without padding: 
        sample_per_wavelength = len(x_data)/(np.max(x_data)-np.min(x_data))
        # magnitudes
        fft_y = np.abs(fft.rfft(y_data))

        # X-axis of fft
        fft_x = fft.rfftfreq(len(y_data), 1/sample_per_wavelength)

    # With zero-padding (better frequency resolution)
        fft_length = int(1e4)
        
        # fft_length = next_fast_len(fft_length)
        # y_padded = np.zeros(fft_length)
        # y_padded[0:len(y_data)] = y_data
        # x_padded = np.linspace(start=x_data[0], stop=fft_length*sample_per_wavelength, num=fft_length)#np.linspace(x_data[0],x_data[len(x_data) -1], num=fft_length)
        # plt.figure()
        # plt.plot(x_padded, y_padded)
        # plt.show()
        # print("NEW SIZE", len(y_padded))
        # Get sample rate relative to x-axis, used for calculating the relative frequency
        # sample_per_wavelength = fft_length/(np.max(x_data)-np.min(x_data))
        y_padded = np.pad(y_data, (0,fft_length-len(y_data)), mode='constant')
        # magnitudes
        fft_y = np.abs(fft.rfft(y_padded))
    
        # X-axis of fft
        fft_x = fft.rfftfreq(len(y_padded), 1/sample_per_wavelength)


        # Remove DC component (offset) and then look for maximum amplitude
        index = np.where(fft_y[1:] == np.max(fft_y[1:]))[0] 
        print(index)
        # plt.figure()
        # plt.stem(fft_x, fft_y)
        # plt.show()
        # Get estimated frequency that will be used as init frequency
        print("Frequency", index[0], fft_x[index])
        frequency_init = fft_x[index]

        # Return as float (type(frequency_init) = np array)
        # if frequency_init[0] <0.01:
        #     return 0
        # else: 
        self.frequency_init_list.append(frequency_init[0])
        return frequency_init[0]
    def get_mse(self, measurement_number, params):
        """ Get mse """
        x_data, y_data = self.get_data(measurement_number)
        prediction = self.sine_prototype_amplitude_offset(x_data,params[0],params[1],params[2], params[3], params[4],params[5])
        return np.mean((prediction - y_data)**2)
    
    def sine_fit_amplitude_offset(self, measurement_number, plot):
        """ Fit on the given prototype
            function_prototype is the function to be optimized
        """
        # Guess frequency
        frequency_init = self.frequency_guess(measurement_number)
        amplitude_init = self.amplitude_guess(measurement_number)
        amplitude_offset_init = amplitude_init # was 0.1
        phase_init = 0

        mse = 1
        count = 0

        lower_limit_frequency = 0.1*frequency_init
        amplitude_init_new = amplitude_init
        amplitude_offset_init_new = amplitude_offset_init
        frequency_init_new = frequency_init
        # 0.05 works for other set
        while count < 1:
            # offset_init = 0
            offset_slope_init, offset_init = self.slope_and_offset_guess(measurement_number, False)
            # Initial guess of parameters, should be estimated carefully
            # [amplitude, amplitude_offset, frequency, phase, offset, offset_slope]
            initial_guess = [amplitude_init_new, amplitude_offset_init_new, frequency_init_new , phase_init, offset_init, offset_slope_init]

            # Get data from sample number
            x_data, y_data = self.get_data(measurement_number)

            # Perform the least squares fit using curve_fit with max iterations of max_iters
            max_iters = 1e7
            optimized_params, _ = curve_fit(self.sine_prototype_amplitude_offset, x_data, y_data, p0=initial_guess, maxfev=int(max_iters))

            # Unpack optimal params
            amplitude_opt, amplitude_offset_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt = optimized_params

            # Emperic determined mse
            mse = self.get_mse(measurement_number, optimized_params)
            if mse<0.4:#0.4
                print("MSE")
                break
            frequency_init = np.random.rand()/10
            while frequency_init < lower_limit_frequency:
                frequency_init = np.random.rand()/10
            if amplitude_opt < 0.5*amplitude_init and amplitude_offset_opt < amplitude_offset_init and frequency_opt < 2*frequency_init:
                print("AMPLITUDE")
                break
            amplitude_init_new = np.random.rand() * amplitude_init /10
            count += 1
        print("Measuerment count", measurement_number, count ,amplitude_init)
        # Make plot of fit and data
        if plot:
             # Get the fitted sine
            x_plot = np.linspace(x_data[0], x_data[len(x_data)-1], 10*len(x_data))
            fitted_sine = self.sine_prototype_amplitude_offset(x_plot, amplitude_opt, amplitude_offset_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt)
            figure = plt.figure()
            plt.title("Sine fit of measurement {}".format(measurement_number))
            plt.scatter(x_data,y_data, label="Original Data")
            plt.plot(x_plot, fitted_sine, color='red', label="Optimized sine")
            plt.xlabel("Wavelength [$nm$]")
            plt.ylabel("Intensity [$\mu W$]")
            plt.legend()
            plt.show()
            self.save_figure(figure, "sinefit_set2.svg")
        return amplitude_opt, amplitude_offset_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt
    
    def sine_fit_phase(self, measurement_number,plot):
        """ Fit on the given prototype
            function_prototype is the function to be optimized
        """
        # Guess frequency 
        frequency_init = self.frequency_guess(measurement_number)
        amplitude_init = self.amplitude_guess(measurement_number)
        phase_init = 0
        offset_init = 0
        offset_slope_init = 0
        offset_slope_init, offset_init = self.slope_and_offset_guess(measurement_number, False)
        # Initial guess of parameters, should be estimated carefully
        # [amp,freq, phase, offset,offset_slope]
        initial_guess = [amplitude_init, frequency_init , phase_init, offset_init, offset_slope_init]

        # Get data from sample number
        x_data, y_data = self.get_data(measurement_number)

        # Perform the least squares fit using curve_fit with max iterations of max_iters
        max_iters = 1e5
        optimized_params, _ = curve_fit(self.sine_prototype_phase, x_data, y_data, p0=initial_guess, maxfev=int(max_iters))

        # Unpack params
        amplitude_opt , frequency_opt, phase_opt, offset_opt, offset_slope_opt = optimized_params

        # Get the fitted sine
        fitted_sine = self.sine_prototype_phase(x_data, amplitude_opt , frequency_opt, phase_opt, offset_opt, offset_slope_opt)

        error=0
        if plot:
            figure = plt.figure()
            plt.title("Fit without amplitude offset of measurement {}".format(measurement_number))
            plt.scatter(x_data,y_data, label="Original Data")
            plt.plot(x_data, fitted_sine, color='red', label="Optimized sine")
            plt.xlabel("Wavelength [nm]")
            plt.ylabel("Intensity [$\mu W$]")
            plt.legend()
            plt.show()
            self.save_figure(figure, "too_high_amplitude.svg")

        return amplitude_opt , frequency_opt, phase_opt, offset_opt, offset_slope_opt
    # def plot_sine_fit(self, measurement_number):
    #     """ Plot fitted sine"""
    def plot_two_sines(self,measurement_number,params_phase, params_amp):
        x_data,y_data = self.get_data(measurement_number)

        fig, ax = plt.subplots(2,1)
        ax[0].set_title("Sine fit of measurement {}".format(measurement_number))
        ax[0].plot(x_data,self.sine_prototype_phase(x_data,params_phase[0],params_phase[1],params_phase[2], params_phase[3], params_phase[4]), label="Phase")
        ax[0].scatter(x_data,y_data, color='red')
        ax[0].legend()
        ax[1].plot(x_data,self.sine_prototype_amplitude_offset(x_data,params_amp[0],params_amp[1],params_amp[2], params_amp[3], params_amp[4],params_amp[5]), label="Amp")
        ax[1].scatter(x_data,y_data, color='red')
        ax[1].legend()
        plt.show()

    def plot_stats(self, fit_type):
        n_measurements= len(self.get_data(0)[0])

        amplitude_list = []
        amplitude_offset_list = []
        frequency_list = []
        phase_list = []
        offset_list = []
        offset_slope_list = []
        mse_list = []
        measurement_number = []

        skewness_list = []
        low = 0
        high = 100
        for i in range(low,high):#n_measurements):
            print(i)

            # Get data
            x_data, y_data = self.get_data(measurement_number=i)

            # Fit
            if fit_type == "phase":
                type_fit = "without amplitude offset"
                amplitude , frequency, phase, offset, offset_slope = self.sine_fit_phase(measurement_number=i,plot=False)
                prediction = self.sine_prototype_phase(x_data, amplitude, frequency, phase, offset, offset_slope)
                amplitude_offset = 0
            else:
                type_fit = "with amplitude offset"
                amplitude, amplitude_offset, frequency, phase, offset, offset_slope = self.sine_fit_amplitude_offset(measurement_number=i, plot=False)
                prediction = self.sine_prototype_amplitude_offset(x_data, amplitude, amplitude_offset, frequency, phase, offset, offset_slope)
            # Store
            amplitude_list.append(amplitude)
            amplitude_offset_list.append(amplitude_offset)
            frequency_list.append(frequency)
            phase_list.append(phase)
            offset_list.append(offset)
            offset_slope_list.append(offset_slope)

            measurement_number.append(i)
            
            mse_list.append(np.mean((prediction - y_data)**2))
            skewness_list.append(frequency/amplitude)

        fig, ax = plt.subplots(4,1, sharex=True)
        fig.suptitle("Fit {} for {} ".format(type_fit, self.data_set) ,fontsize=14)
        ax[0].set_title('Frequency',fontsize=8)
        ax[0].plot(measurement_number, np.abs(frequency_list), marker='+', label="Optimized frequency")
        ax[0].set_ylabel('$m^{-1}$')
        points = [54,66]
        freq_plot = []
        # for i in points:
        #     freq_plot.append(frequency_list[i])
        # ax[0].scatter(points, np.abs(freq_plot), color='red', label="Two types of mis-fits")
        print(len(measurement_number), len(self.frequency_init_list))
        ax[0].plot(measurement_number, self.frequency_init_list, marker='+', label="Estimated frequency (fft)")
        ax[0].legend(loc='upper left')
        self.frequency_init_list.clear()

        ax[1].set_title('Amplitude (standardized)',fontsize=8)
        ax[1].plot(measurement_number, np.abs(amplitude_list), marker="+", label="amplitude")
        ax[1].set_ylabel('$\mu W$')

        ax[2].set_title('Amplitude Offset (standardized)',fontsize=8)
        ax[2].plot(measurement_number, np.abs(amplitude_offset_list), marker="+", label='amplitude offset')
        ax[2].set_ylabel('$\mu W$')

        ax[3].set_title('MSE (standardized)',fontsize=8)
        ax[3].plot(measurement_number, mse_list, marker="+", label= 'mse')
        ax[3].set_xlabel('Measurement #')
        ax[3].set_ylabel('$(\mu W)^2$')
        # ax[1].set_ylim(-0.01,0.09)
        # ax[2].set_ylim(900,1700)
        # ax[3].set_ylim(-0.01,0.07)
        ears = [73,76,78,80,81,83,85,86,88,89,90,91,93,94,96,97]
        asymetric = [20,24,29,30,32,36,45,47,48]
        period = [14,19,21,28,33,37,44]
    
        # for i in ears:
        #     if i>low:
        #         ax[0].scatter(i,np.abs(frequency_list[i]), color='magenta')
        #         ax[1].scatter(i,np.abs(amplitude_list[i]), color='magenta')
        # for i in asymetric:
        #     if i>low:
        #         ax[0].scatter(i,np.abs(frequency_list[i]), color='darkgreen')
        #         ax[1].scatter(i,np.abs(amplitude_list[i]), color='darkgreen')
        # for i in period:
        #     if i>low:
        #         ax[0].scatter(i,np.abs(frequency_list[i]), color='red')
        #         ax[1].scatter(i,np.abs(amplitude_list[i]), color='red')



        for i in range(4):
            # ax[i].legend()
            ax[i].grid()
       
        plt.show()
        return fig

    def interpolation(self, measurement_number):
        x_data, y_data = self.get_data(measurement_number)
        print(len(y_data))

        interpolation = CubicSpline(x_data, y_data)
        print("len", len(x_data))
        x_interpolate = np.linspace(x_data[0], x_data[len(x_data)-1], num=10*len(x_data))
        y_interpolate = interpolation(x_interpolate)

        # fig, ax = plt.subplots(2,1)
        # ax[0].scatter(x_data,y_data)
        # ax[1].scatter(x_interpolate,y_interpolate)
        # plt.show()

        # plt.figure()
        # plt.scatter(x_data,y_data)
        # plt.scatter(x_interpolate, interpolation(x_interpolate), color='red')
        # plt.show()
        # self.sine_fit_amplitude_offset(measurement_number, True)
        return x_interpolate, y_interpolate

    def save_figure(self,fig, image_name):
        # image_name = "sine_fit.svg"
        image_format = "svg"
        fig.savefig(image_name, format=image_format, dpi=1200)

if __name__ == "__main__":
    fit_set1 = SineFit(filename="20210523-113619.txt", data_set ='Data-set1', data_type='Warner')
    fit_set2 = SineFit(filename="20210523-142009.txt", data_set ='Data-set2', data_type='Warner')
    fit_set3 = SineFit(filename="20210523-113619_1.txt", data_set ='Data-set1', data_type='Warner')
    fit_set4 = SineFit(filename="20210523-142009_1.txt", data_set ='Data-set2', data_type='Warner')
    
    # fit_joost = SineFit(filename ='rampcm.csv', data_set="Ramp cm", data_type='Joost')
    
    # fit_set1.sine_fit_amplitude_offset(2, True)
    fit_set1.plot_stats('amplitude')
    fit_set1.sine_fit_amplitude_offset(0, True)
    fit_set1.sine_fit_amplitude_offset(1, True)
    fit_set1.sine_fit_amplitude_offset(2, True)
    # for i in range(100):
    #     # x_interpolated, y_interpolated = fit_set2.interpolation(i)
    #     # fit_set2.set_data(i, y_interpolated)
    #     fit_set2.sine_fit_amplitude_offset(i,True)
    # sys.exit()
    # fit_set1.plot_measurement(50)
    # fit_set4.plot_measurement(50)

    # fit_set2.sine_fit_phase(66, True)
    # figure = fit_set1.plot_stats('phase')
    # fit_set1.save_figure(figure, 'plot_stats_phase_set1.svg')
    # fit_set2.save_figure(figure, 'plot_stats_phase_set2.svg')
    # fit_set2.plot_stats('phase')
    # fit_set1.plot_stats('amplitude')
    # fit_set2.plot_stats('amplitude')
    # fit_set2.sine_fit_phase(4, True)
    
    # for i in range(0,100):
    #     # fit_set1.sine_fit_amplitude_offset(i,True)
    #     x_interpolated, y_interpolated = fit_set2.interpolation(i)
    #     fit_set2.set_data(i, y_interpolated)
    #     fit_set2.sine_fit_phase(i, True)
        # x_interpolated, y_interpolated = fit_set2.interpolation(i)
        # fit_set2.set_data(i, y_interpolated)
    sys.exit()
    # fit_set1.sine_fit_amplitude_offset(30, True)
    # fit_set1.plot_stats()
    fit_set2.plot_stats('phase')
    # fit_set2.plot_stats()
    
    fit_set2.plot_measurement(50)

    for i in range(10,60):
        print(fit_set1.sine_fit_amplitude_offset(i, True))
    # fit_set1.sine_fit_amplitude_offset(30,True)
    # fit_set1.sine_fit_phase(30,True)
    # sys.exit()
    wrong_fits = [20, 52, 55, 45, 57, 69]
    # Get n measurements
    n_measurements = len(fit_set1.get_data(1)[0])
    print("number of measurements", n_measurements)

    frequencies = []
    amplitudes = []
    frequencies_2 = []
    amplitudes_2 = []
    measurement_number = []
    errors = []

    # fit_set1.sine_fit_amplitude_offset(20,True)
    # fit_set1.plot_two_sines(52,True)
    ears = [73,76,78,80,81,83,685,86,88,89,90,91,93,94,96,97]
    asymetric = [20,24,29,30,32,36,45,47,48]
    period = [14,19,21,28,33,37,44]
    mse_others = []
    mse_ears = []
    mse_asymetric = []
    mse_period = []
    # for i in range(100):
    #     # fit_set1.slope_and_offset_guess(i, True)
    #     x_data, y_data = fit_set1.get_data(i)
    #     params_amp = fit_set1.sine_fit_amplitude_offset(i, True)
    #     prediction = fit_set1.sine_prototype_amplitude_offset(x_data, params_amp[0],params_amp[1],params_amp[2], params_amp[3], params_amp[4],params_amp[5])
    #     mse = np.mean((prediction - y_data)**2)
    #     if i in ears:
    #         mse_ears.append(mse)
    #     elif i in asymetric:
    #         mse_asymetric.append(mse)
    #     elif i in period:
    #         mse_period.append(mse)
    #     else:
    #         mse_others.append(mse)
    #     print(params_amp)
    #     # params_phase = fit_set1.sine_fit_phase(i, False)
    #     # fit_set1.plot_two_sines(i,params_phase,params_amp)
    # print("MSE others", np.mean(mse_others))
    # print("MSE ears", np.mean(mse_ears))
    # print("MSE asymetric", np.mean(mse_asymetric))
    # print("MSE period", np.mean(mse_period))
    # sys.exit()
    
    for i in range(n_measurements):
        print(i)

        # Get data
        x_data, y_data = fit_set1.get_data(measurement_number=i)

        # Fit
        amplitude, amplitude_offset, frequency, phase, offset, offset_slope = fit_set1.sine_fit_amplitude_offset(measurement_number=i, plot=False)

        amplitudes.append(amplitude)
        frequencies.append(frequency)

        amplitude, amplitude_offset, frequency, phase, offset, offset_slope = fit_set2.sine_fit_amplitude_offset(measurement_number=i, plot=False)

        amplitudes_2.append(amplitude)
        frequencies_2.append(frequency)
        # Store
        
        measurement_number.append(i)
        # if error == 1:
        #     errors.append(i)

    fig, ax = plt.subplots(2,2)
    # plt.title("Frequencies")
    ax[0,0].plot(measurement_number, np.abs(frequencies), marker='+')
    ax[0,0].set_title("Optimized Frequency per Measurement(set1)")
    ax[1,0].set_title("Optimized Frequency per Measurement(set2)")
    ax[0,0].legend()
    # plt.plot(measurement_number, amplitudes)
    # ax[0].set_xlabel("Measurement number")
    ax[0,0].set_ylabel(" Relative Frequency [Periods/Wavelength]")
    ax[0,0].grid()
    
    # ax[1].title("Amplitudes")
    # plt.plot(measurement_number, frequencies, marker='+')
    ax[1,0].plot(measurement_number, np.abs(amplitudes), marker="+")
    ax[1,0].set_title("Optimized Amplitude per Measurement (set1)")
    ax[1,1].set_title("Optimized Amplitude per Measurement (set2)")
    
    ax[1,1].plot(measurement_number, np.abs(amplitudes_2), marker="x")
    ax[0,1].plot(measurement_number, np.abs(frequencies_2), marker='x')

    ax[1,0].set_xlabel("Measurement number")
    ax[1,0].set_ylabel("Amplitude [V]")
    ax[1,0].legend()
    ax[1,0].grid()
    ax[1,1].grid()
    ax[0,1].grid()
    plt.show()

