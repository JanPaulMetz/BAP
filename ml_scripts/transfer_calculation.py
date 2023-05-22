"""Module for calculating transfer functions"""
import numpy as np
from calculate_fft import *
from generate_data import generate_data
import matplotlib.pyplot as plt
from scipy import signal

def get_bin_size(frequency, periods_per_bin, sample_rate):
    """Get sample size based on input frequency and required periods per sample"""
    period_t = 1/frequency
    bin_n = period_t*sample_rate*periods_per_bin
    return bin_n

#TODO: Improve run time 
def scale_axis(axis, new_bin_size):
    """Scale omega axis to desired bin size"""
    original_size = axis.size
    bin_ratio = new_bin_size / original_size

    axis_scaled = np.zeros(new_bin_size)
    for i in range(original_size):
        axis_scaled[int(i*bin_ratio)] = axis[i]
    return axis_scaled

def get_log_space(start, stop, n_sweeps):
    """ get logspace between 1-stop or start-stop if start = 0"""
    if start == 0:
        start_log = np.log10(1)
        stop_log = np.log10(stop)
    else: 
        start_log = np.log10(start)
        stop_log = np.log10(stop)
    log = np.logspace(start_log,stop_log,n_sweeps)
    return log

def get_duration(bin_size, sample_rate):
    """Get duration bassed on sample_size and sample_rate"""
    duration = bin_size/sample_rate
    return duration

def frequency_sweep(start, stop, sample_rate, duration, n_sweeps):
    "Sweep over frequency"
    # Get sweep setp_size :
    step_size = int((stop-start)/n_sweeps)
    # duration = n_samples/sample_rate
    n_samples = int(duration*sample_rate)
    # print("n_samples:", n_samples)
    sweeped_data_out = np.empty((n_sweeps,n_samples))
    sweeped_data_in = np.empty((n_sweeps,n_samples))
    i = 0
    # print("Range : ", range(start,stop,step_size))
    # TODO: sweep log instead of linear
    start_log = np.log10(1)
    stop_log = np.log10(stop)
    log = np.logspace(start_log,stop_log,n_sweeps)
    
    # print("log_space", log)

    for index, frequency in enumerate(log):
        # print("f", frequency)
        data_in, time_axis, data_out = generate_data(frequency, sample_rate, duration)
        # Make sure index inside bounds (step_size)
        if i < step_size:
            sweeped_data_out[i, :] = data_out
            sweeped_data_in[i, :] = data_in
        i += 1
    return sweeped_data_in, sweeped_data_out, time_axis#, log

    # lin = np.linspace(start,stop,n_sweeps)
    # for frequency in range(start, stop, step_size):
    #     # print("f", frequency)
    #     # For each frequency generate a singal sequence and store in sweeped
    #     data_in, time_axis, data_out = generate_data(frequency, sample_rate, duration)
    #     # Make sure index inside bounds (step_size)
    #     if i < step_size:
    #         sweeped_data_out[i, :] = data_out
    #         sweeped_data_in[i, :] = data_in
    #     i += 1
    # return sweeped_data_in, sweeped_data_out, time_axis
def get_transfer_power():
    """Get transfer function by deviding power"""
    # system constants:
    start = 20e3
    stop = 1.3e6
    sample_rate = 65e6
    periods_per_bin = 2
    n_sweeps = 50

    # maximum bin size
    # max_bin_size = get_bin_size(start, periods_per_bin, sample_rate)
    # max_bin_size = np.ceil(max_bin_size)
    
    # get array containing bin sizes
    bin_logspace = get_log_space(start, stop, n_sweeps)
    
    # get omega axis
    bin_size = get_bin_size(start, periods_per_bin, sample_rate)
    duration = get_duration(bin_size, sample_rate)
    data_in, time_axis, data_out = generate_data(start, sample_rate, duration)
    omega_init, fft_init = calculate_signal_fft(time_axis, data_in, sample_rate)

    # max bin size
    max_bin_size = omega_init.size

    # initialize data bins
    data_in_fft = np.zeros((n_sweeps, int(max_bin_size)))
    data_out_fft = np.zeros((n_sweeps, int(max_bin_size)))
    magnitude_response = np.zeros((n_sweeps, int(max_bin_size)))
    phase_response = np.zeros((n_sweeps, int(max_bin_size)))
    index_max = np.zeros(n_sweeps, dtype=int)
    # Loop for each bin size (or frequency)
    for i, frequency in enumerate(bin_logspace):
        # Get bin size and duration
        bin_size = get_bin_size(frequency, periods_per_bin, sample_rate)
        duration = get_duration(bin_size, sample_rate)

        # get time data
        data_in, time_axis, data_out = generate_data(frequency, sample_rate, duration)

        # get fft
        omega_in, fft_in = calculate_signal_fft(time_axis, data_in, sample_rate)
        omega_out, fft_out = calculate_signal_fft(time_axis, data_out, sample_rate)
        
        # Get phase response phase(H) = arctan(Im(H)/Re(H))
        # nonzero = np.where(np.abs(fft_in)>0)
        fft_in_ph = scale_axis(fft_in, max_bin_size)
        fft_out_ph = scale_axis(fft_out, max_bin_size)
        nonzero_in = np.where(fft_in_ph!=0)
        transfer = np.zeros(max_bin_size)
        transfer[nonzero_in] = fft_out_ph[nonzero_in]/fft_in_ph[nonzero_in]
        print(transfer)
        # transfer = scale_axis(transfer, max_bin_size)
      
        #scale

        phase_response[i,:] = np.arctan2(np.imag(transfer),np.real(transfer))
        # scale fft to max bin size
        data_in_fft[i,:] = scale_axis(np.abs(fft_in), max_bin_size)
        data_out_fft[i,:] = scale_axis(np.abs(fft_out), max_bin_size)
        
        # Store max index of input fft
        print("DEBUG", np.where(data_in_fft[i,:] == np.max(data_in_fft[i,:]))[0] )
        index_max[i] = int(np.where(data_in_fft[i,:] == np.max(data_in_fft[i,:]))[0])

        # get total power output fft
        input_power = data_in_fft[i,index_max[i]]
        output_power = data_out_fft[i,index_max[i]]
        
        print("POWER", input_power, output_power)
        power_mag_response = output_power/input_power

        # Store it at index max power input
        print(index_max[i])
        magnitude_response[i,int(index_max[i])] = power_mag_response
        # magnitude_response[i,:] = calculate_transfer_magnitude(data_in_fft[i,:], data_out_fft[i,:])
        # print(1)
        # plt.figure()
        # plt.stem(omega_init, data_in_fft[i,:])
        # plt.scatter(omega_init, data_out_fft[i,:], color='r')
        # plt.show()
    print("Pgase size", magnitude_response.shape)
    magnitude_tf_mean, magnitude_tf_indices = mean_transfer(magnitude_response)
    print("Pgase size", phase_response.shape)
    phase_tf_mean, phase_tf_indices = mean_transfer(phase_response)
    print("Pgase size", phase_response.shape)
    # Validation
    print(magnitude_response.shape)
    print(omega_init.shape)
    f_cutoff = 500_000
    num, den = signal.butter(1, [f_cutoff], analog=False,btype='lowpass', fs=sample_rate)
    w,h = signal.freqz(num, den)
    w_lin = np.linspace(0,sample_rate/2, num=512)
    print("Outliers: ",np.where((np.rad2deg(phase_tf_mean)>-15) & (omega_init > 6e5) & (np.abs(phase_tf_mean)>0) ))
    outliers = np.where((np.rad2deg(phase_tf_mean)>-15) & (omega_init > 6e5) & (np.abs(phase_tf_mean)>0) )
    plt.figure()
    plt.scatter(omega_init[outliers],  np.rad2deg(phase_tf_mean[outliers]), color='red')
    plt.scatter(omega_init[phase_tf_indices], phase_tf_mean[phase_tf_indices], marker='.', color='green', label="Measured Response")
    plt.semilogx(w_lin,  np.rad2deg(np.unwrap(np.angle(h))), ls='dashed', label='Simulated Response')
    plt.grid(which='both', axis='both')
    plt.vlines(500_000,ymin=0, ymax=-8, ls='dashed', color='green',label="-3dB frequency")
    plt.hlines(-3,xmin=start, xmax=stop, ls='dashed', color='green')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.legend()
    plt.show()
    plt.figure()
    plt.scatter(omega_init[magnitude_tf_indices], 20*np.log10(magnitude_tf_mean[magnitude_tf_indices]), marker='.', color='red', label="Measured Response")
    plt.semilogx(w_lin,  20*np.log10(np.abs(h)), ls='dashed', label='Simulated Response')
    plt.grid(which='both', axis='both')
    plt.vlines(500_000,ymin=0, ymax=-8, ls='dashed', color='green',label="-3dB frequency")
    plt.hlines(-3,xmin=start, xmax=stop, ls='dashed', color='green')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.legend()
    plt.show()
    
def get_transfer_dev():
    """ Get transfer function"""
    # system constants:
    start = 20e3
    stop = 1.3e6
    sample_rate = 65e6
    periods_per_bin = 10
    n_sweeps = 200

    # maximum bin size
    # max_bin_size = get_bin_size(start, periods_per_bin, sample_rate)
    # max_bin_size = np.ceil(max_bin_size)
    
    # get array containing bin sizes
    bin_logspace = get_log_space(start, stop, n_sweeps)
    
    # get omega axis
    bin_size = get_bin_size(start, periods_per_bin, sample_rate)
    duration = get_duration(bin_size, sample_rate)
    data_in, time_axis, data_out = generate_data(start, sample_rate, duration)
    omega_init, fft_init = calculate_signal_fft(time_axis, data_in, sample_rate)

    # max bin size
    max_bin_size = omega_init.size

    # initialize data bins
    data_in_fft = np.zeros((n_sweeps, int(max_bin_size)))
    data_out_fft = np.zeros((n_sweeps, int(max_bin_size)))
    magnitude_response = np.zeros((n_sweeps, int(max_bin_size)))
    phase_response = np.zeros((n_sweeps, int(max_bin_size)))

    # Loop for each bin size (or frequency)
    for i, frequency in enumerate(bin_logspace):
        # Get bin size and duration
        bin_size = get_bin_size(frequency, periods_per_bin, sample_rate)
        duration = get_duration(bin_size, sample_rate)

        # get time data
        data_in, time_axis, data_out = generate_data(frequency, sample_rate, duration)

        # get fft
        omega_in, fft_in = calculate_signal_fft(time_axis, data_in, sample_rate)
        omega_out, fft_out = calculate_signal_fft(time_axis, data_out, sample_rate)

        # Calculate magnitude:
        # magnitude_response_unscaled = calculate_transfer_magnitude(fft_in, fft_out)

        # Scale axis to fit in max bin size
        # magnitude_response[i,:] = scale_axis(magnitude_response_unscaled, max_bin_size)

       
        # scale fft to max bin size
        data_in_fft[i,:] = scale_axis(np.abs(fft_in), max_bin_size)
        data_out_fft[i,:] = scale_axis(np.abs(fft_out), max_bin_size)
        
        magnitude_response[i,:] = calculate_transfer_magnitude(data_in_fft[i,:], data_out_fft[i,:])
        # print(1)
        # plt.figure()
        # plt.stem(omega_init, data_in_fft[i,:])
        # plt.scatter(omega_init, data_out_fft[i,:], color='r')
        # plt.show()
     # Get mean of transfer matrix (convert to 1 TF)
    magnitude_tf_mean, magnitude_tf_indices = mean_transfer(magnitude_response)

    # plt.figure()
    # plt.stem(omega_init, magnitude_response[25,:])
    # # plt.scatter(omega_init, data_out_fft[i,:], color='r')
    # plt.show()

    # Validation
    f_cutoff = 500_000
    num, den = signal.butter(1, [f_cutoff], analog=False,btype='lowpass', fs=sample_rate)
    w,h = signal.freqz(num, den)
    w_lin = np.linspace(0,sample_rate/2, num=512)
    plt.figure()
    plt.scatter(omega_init[magnitude_tf_indices], 20*np.log10(magnitude_tf_mean[magnitude_tf_indices]), marker='.', color='red')
    plt.semilogx(w_lin,  20*np.log10(np.abs(h)), ls='dashed', label='Simulated Response')
    plt.grid(which='both', axis='both')
    plt.vlines(500_000,ymin=0, ymax=-8, ls='dashed', color='green')
    plt.hlines(-3,xmin=start, xmax=stop, ls='dashed', color='green')
    plt.show()


def get_transfer(time_axis, data_in, data_out, sample_rate, duration):
    """ Calculate magnitude and phase response using sweeped signal
        data_in and data_out are already sweeped and scaled
    """
    # Some constants:
    n_sweeps = data_in.shape[0]
    n_samples = int(duration*sample_rate)

    # Init arrays: SIZE!!
    data_in_fft = np.empty((n_sweeps, n_samples), dtype='complex_')
    data_out_fft = np.empty((n_sweeps, n_samples), dtype='complex_')
    magnitude_response = np.empty(
        (n_samples, int(0.5*n_samples)))  # , dtype='complex_'
    phase_response = np.empty((n_samples, int(0.5*n_samples)))
    """ DEV: WINDOWING (HANN)"""

    """ END DEV: WINDOWING"""
    # Calculate fft and then magnitude and frequency response
    for i in range(n_sweeps):
         # Get bin size and duration
        """DEV"""
        
        """END DEV"""
        data_in_fft[i, :] = calculate_signal_fft(
            time_axis, data_in[i, :], sample_rate)[1]
        data_out_fft[i, :] = calculate_signal_fft(
            time_axis, data_out[i, :], sample_rate)[1]
        magnitude_response[i, :] = calculate_transfer_magnitude(
            data_in_fft[i, :], data_out_fft[i, :])
        phase_response[i, :] = calculate_transfer_phase(
            data_in_fft[i, :], data_out_fft[i, :])

    # Get omega axis
    omega = calculate_signal_fft(time_axis, data_in[0, :], sample_rate)[0]

    # Get single sided omega axis
    omega_single_out = fft_to_singlesided(
        omega, data_out_fft[0, :], sample_rate, duration)[0]

    # Get max index (For testing)
    # max_index = get_max_index(40, stop_freq, omega_single_out)

    # Get only nonzero elements
    magnitude_response_mean, nonzero_ind_magnitude = mean_transfer(
        magnitude_response)
    magnitude_response_mean = magnitude_response_mean[nonzero_ind_magnitude]
    phase_response_mean, nonzero_ind_phase = mean_transfer(phase_response)
    phase_response_mean = phase_response_mean[nonzero_ind_phase]

    # Get nonzero omega axis
    omega_magnitude_response = omega_single_out[nonzero_ind_magnitude]
    omega_phase_response = omega_single_out[nonzero_ind_phase]

    return magnitude_response_mean, omega_magnitude_response, phase_response_mean, omega_phase_response

def calculate_transfer_magnitude_dev(input_fft, output_fft):
    """First calculate complex TF, then take magnitude"""
    # calculate transfer
    print("shapes out in", output_fft.shape, input_fft.shape)
    transfer_function = np.divide(np.abs(output_fft), np.abs(input_fft), dtype='complex_')
    print("shape tf", transfer_function.shape)
    print("tf ", transfer_function)
    transfer_magnitude = (transfer_function)
    print("tm", transfer_magnitude)
    return transfer_magnitude

def calculate_transfer_magnitude(input_fft, output_fft):
    """Calculates transfer magnitude |H(s)| = |Y(s)|/|X(s)| numeric of 1 sample
    Inputs are magnitudes: Maybe include getting the magnitude in this function
    """
    # Get abs value
    input_fft = np.abs(input_fft)
    output_fft = np.abs(output_fft)
    # Get indeces of input_fft where nonzero
    nonzero_indices = [index for index,
                       value in enumerate(input_fft) if value > 0.01]

    # H(s) = Y(s)/X(s)
    nonzero_transfer_function = np.divide(
        output_fft[nonzero_indices], input_fft[nonzero_indices])
    transfer_function = np.zeros(np.shape(input_fft))  # , dtype='complex_'

    j_max = nonzero_transfer_function.size
    i = 0
    j = 0
    # Fil in nonzero values in transferfunction
    while j < j_max:
        if i == nonzero_indices[j]:
            transfer_function[i] = nonzero_transfer_function[j]
            # increment j if index is taken
            j += 1
        # increment i every loop
        i += 1
    # Only return left half (n_samples/2),
    # since right half is mirrored image
    n_samples = input_fft.size#0.5*input_fft.size
    return transfer_function[0:int(n_samples)]


def calculate_transfer_phase(input_fft, output_fft):
    """Calculate phase response of the transfer function phase(H) = arctan(Im(H)/Re(H))
    Input arguments are the raw fft
    """
    # Get indeces of input_fft where nonzero, Maybe ude np.where()?
    nonzero_indices = [index for index, value in enumerate(
        input_fft) if np.abs(value) > 0.01]
    nonzero_transfer_function = np.divide(
        output_fft[nonzero_indices], input_fft[nonzero_indices])

    # phase(H) = arctan(Im(H)/Re(H))
    nonzero_phase = np.arctan(np.divide(
        np.imag(nonzero_transfer_function), np.real(nonzero_transfer_function)))
    transfer_function = np.zeros(np.shape(input_fft))

    j_max = nonzero_transfer_function.size
    i = 0
    j = 0
    # Fil in nonzero values in transferfunction
    while j < j_max:
        if i == nonzero_indices[j]:
            # print("j", j)
            transfer_function[i] = nonzero_phase[j]
            # increment j if index is taken
            j += 1
        # increment i every loop
        i += 1

    # Get H: H = output_fft/ input_fft: DONT KNOW IF THIS IS CORRECT!
    n_samples = input_fft.size
    return transfer_function[0:int(n_samples)]

# TODO: CHECK FOR OUTLIERS

def mean_transfer_dev(transfer_matrix):
    mean_transfer = np.mean(transfer_matrix, axis=0)
    return mean_transfer

def mean_transfer(transfer_matrix):
    """Take mean of all non-zero values per column"""
    mean_transfer_list = []
    # print("SHAPE t matrix", transfer_matrix.shape)
    for i in range(transfer_matrix.shape[1]):  # For all columns
        # Copy nonzero row
        nonzeros_row = transfer_matrix[np.abs(
            transfer_matrix[:, i]) > 0.5*np.max(transfer_matrix[:,i])]  # Store all nonzeros
        # Get nonzero terms
        nonzeros = nonzeros_row[np.abs(nonzeros_row) > 0.015]
        # if empty slice:
        if len(nonzeros) == 0:
            nonzeros = 0
        # MAYBE CHECK FOR OUTLIERS?
        nonzeros_mean = np.mean(nonzeros)
        mean_transfer_list.append(nonzeros_mean)

    mean_transfer_array = np.array(mean_transfer_list)
    # Get nonzero indeces
    nonzero_ind = np.where(np.abs(mean_transfer_array) > 0.0)

    return mean_transfer_array, nonzero_ind

def remove_below_treshold(transfer_matrix):
    treshold = 0.1
    transfer_matrix = np.abs(transfer_matrix)
    max_val = np.max(transfer_matrix,axis=1)
    treshold_val = treshold*max_val

    cleaned_transfer_matrix = np.empty((transfer_matrix.shape))

    for row in range(transfer_matrix.shape[0]):#per row
        # Get row
        transfer_row = transfer_matrix[row,:]
        # Get nonzero values and zero indices
        nonzero_values = transfer_row[transfer_row>treshold_val[row]]
        nonzero_indeces = np.where(transfer_row>treshold_val[row])
        # Store zero values and nonzero values: 
        cleaned_transfer_matrix[row,nonzero_indeces] = nonzero_values
    return cleaned_transfer_matrix, nonzero_indeces
