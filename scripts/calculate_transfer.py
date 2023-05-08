"""This module calculates transfer function using input and output"""
import numpy as np
from scipy import signal 
from cmath import phase

from random_plant import *
from generate_data import *

def calculate_transfer_magnitude(input_fft, output_fft):
    """Calculates transfer magnitude |H(s)| = |Y(s)|/|X(s)| numeric of 1 sample
    Inputs are magnitudes: Maybe include getting the magnitude in this function
    """
    # Get abs value
    input_fft = np.abs(input_fft)
    output_fft = np.abs(output_fft)
    # Get indeces of input_fft where nonzero
    nonzero_indices = [index for index, value in enumerate(input_fft) if value>0.01]

    # H(s) = Y(s)/X(s)
    nonzero_transfer_function = np.divide(output_fft[nonzero_indices], input_fft[nonzero_indices])
    transfer_function = np.zeros(np.shape(input_fft), dtype='complex_')

    j_max = nonzero_transfer_function.size
    i = 0
    j = 0
    # Fil in nonzero values in transferfunction
    while j<j_max:
        if i == nonzero_indices[j]:
            transfer_function[i] = nonzero_transfer_function[j]
            # increment j if index is taken
            j += 1
        # increment i every loop
        i += 1
    # Only return left half (n_samples/2),
    # since right half is mirrored image
    n_samples = 0.5*input_fft.size
    return transfer_function[0:int(n_samples)]

def calculate_transfer_phase(input_fft, output_fft):
    """Calculate phase response of the transfer function phase(H) = arctan(Im(H)/Re(H))
    Input arguments are the raw fft
    """
    # Get indeces of input_fft where nonzero, Maybe ude np.where()?
    nonzero_indices = [index for index, value in enumerate(input_fft) if np.abs(value)>0.01]
    nonzero_transfer_function = np.divide(output_fft[nonzero_indices], input_fft[nonzero_indices])
    # print("Nonzero INd",nonzero_indices)
    # phase(H) = arctan(Im(H)/Re(H))
    nonzero_phase = np.arctan(np.divide(np.imag(nonzero_transfer_function), np.real(nonzero_transfer_function)))
    # nonzero_phase = np.angle(nonzero_transfer_function)
    # print("nonzero phase", nonzero_phase)
    transfer_function = np.zeros(np.shape(input_fft), dtype='complex_')

    j_max = nonzero_transfer_function.size
    i = 0
    j = 0
    # Fil in nonzero values in transferfunction
    while j<j_max:
        if i == nonzero_indices[j]:
            # print("j", j)
            transfer_function[i] = nonzero_phase[j]
            # increment j if index is taken
            j += 1
        # increment i every loop
        i += 1
    
    # Get H: H = output_fft/ input_fft: DONT KNOW IF THIS IS CORRECT!
    n_samples = 0.5*input_fft.size
    return transfer_function[0:int(n_samples)]

def get_transfer(time_axis, data_in, data_out, sample_rate, stop_freq, duration):
    """Calculate magnitude and phase response using sweeped signal"""
    # Some constants:
    n_sweeps = data_in.shape[0]
    n_samples = int(duration*sample_rate)

    # Init arrays: SIZE!!
    data_in_fft = np.empty((n_sweeps,n_samples), dtype='complex_')
    data_out_fft = np.empty((n_sweeps,n_samples),dtype='complex_')
    magnitude_response = np.empty((n_samples, int(0.5*n_samples)))
    phase_response = np.empty((n_samples, int(0.5*n_samples)))

    # Calculate fft and then magnitude and frequency response
    for i in range(n_sweeps):
        data_in_fft[i,:] = calculate_signal_fft(time_axis, data_in[i,:], sample_rate)[1]
        data_out_fft[i,:] = calculate_signal_fft(time_axis, data_out[i,:], sample_rate)[1]
        magnitude_response[i,:] = calculate_transfer_magnitude(data_in_fft[i,:], data_out_fft[i,:])
        phase_response[i,:] = calculate_transfer_phase(data_in_fft[i,:], data_out_fft[i,:])
    
    # Get omega axis
    omega = calculate_signal_fft(time_axis, data_in[0,:], sample_rate)[0]

    # Get single sided omega axis
    omega_single_out = fft_to_singlesided(omega, data_out_fft[0,:], sample_rate, duration)[0]
    
    # Get max index (For testing)
    max_index = get_max_index(40, stop_freq, omega_single_out)

    # Get only nonzero elements
    magnitude_response_mean, nonzero_ind_magnitude = mean_transfer(magnitude_response)
    magnitude_response_mean = magnitude_response_mean[nonzero_ind_magnitude]
    phase_response_mean, nonzero_ind_phase = mean_transfer(phase_response)
    phase_response_mean = phase_response_mean[nonzero_ind_phase]
    
    # Get nonzero omega axis
    print(omega_single_out.size)
    print("OMEGA: ", omega_single_out)
    omega_magnitude_response = omega_single_out[nonzero_ind_magnitude]
    print("OMEGA SINGLE", omega_magnitude_response)
    omega_phase_response = omega_single_out[nonzero_ind_phase]

    return magnitude_response_mean, omega_magnitude_response, phase_response_mean, omega_phase_response

#TODO: CHECK FOR OUTLIERS
def mean_transfer(transfer_matrix):
    """Take mean of all non-zero values per column"""
    mean_transfer_list = []
    # print("SHAPE t matrix", transfer_matrix.shape)
    for i in range(transfer_matrix.shape[1]): # For all columns
        # Copy nonzero row
        nonzeros_row = transfer_matrix[np.abs(transfer_matrix[:,i]) > 0] # Store all nonzeros
        # Get nonzero terms
        nonzeros = nonzeros_row[np.abs(nonzeros_row) > 0]
        # if empty slice:
        if len(nonzeros) == 0:
            nonzeros = 0
        # MAYBE CHECK FOR OUTLIERS?
        nonzeros_mean = np.mean(nonzeros)
        mean_transfer_list.append(nonzeros_mean)

    mean_transfer_array = np.array(mean_transfer_list)
    # Get zero indeces
    # zero_ind = np.empty((mean_transfer_array.size),1)
    nonzero_ind = np.where(np.abs(mean_transfer_array) > 0)
    # print(zero_ind)
    return mean_transfer_array, nonzero_ind
