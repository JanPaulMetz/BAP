""" Module containing functions used by the data_processing() thread
    1. message_to_float
    2. 

"""

import numpy as np
from collections import deque
from bitstring import BitArray
from scipy.fft import fft
def message_to_float(message_binary):
    """ Convert 14 bit to half precision floating point
        Actual size is 15 bits since it is unsigned
        So, 15th bit is always 0

        Example: message_binary = 01101 010101010 = 0.333
        sign bit = 0 by definition
        message_binary[0:5] = 01101       (exponent, 5 bits)
        message_binary[5:]  = 010101010   (fraction, 9 bits)
    """
    # If received from test
    if len(message_binary) == 16:
        message_float = message_binary.float

    # If received form fpga -> 14 bits excluding sign bit (always 0)
    else:
        # Get exponent
        exponent_bias = 15
        exponent = message_binary[0:5].uint
        # print("exp",len(message_binary[0:5]))

        # Get fraction
        max_fraction = 2**9
        fraction = message_binary[5:].uint
        # print("frac", len(message_binary[5:]))
        
        # Calculate float
        message_float = (2**(exponent-exponent_bias))*(1+fraction/max_fraction)
    return message_float

def single_point_to_decimal(package_binary):
    """ Convert two's complement to float """
    # If first bit is 1
    if package_binary[0] == 1:
        # print(~package_binary)
        decimal = ~package_binary
    
        return -(decimal.uint +1)/(2**len(package_binary))
    else:
        return (package_binary.uint)/(2**len(package_binary))

# print(twos_complement_to_decimal(BitArray("0b11100101")))

def get_fft_index(frequency, sample_rate, bin_size):
    """ Get index at which this frequency component is placed 
        after performing a DTFT
    """
    # Calculate frequency spacing
    delta_f = sample_rate/bin_size
    # Calculate the bin_number (is the index)
    bin_number = np.divide(frequency,delta_f)
    bin_number = np.round(bin_number)

    return bin_number


def calculate_magnitude_response_a(output_fft_normalized, input_amplitude, index):
    """ Calculate power of input time signal and output normalized fft
        Using Rayleigh Energy theorem (Parseval's theorem), obtain power around index
        Then calculate magnitude response |H(f)| = |Y(s)|/|X(s)| = Py/Px
        Py = sum(|Y(s)|**2)
        Px = A**2 /2
        Return magnitude response of one frequency component
    """
    # Samples around index
    n_around_index = 2
    upper_index = int(index + n_around_index)
    lower_index = int(index - n_around_index)
    # Get fft around index
    output_fft_around_index = np.abs(output_fft_normalized[lower_index:upper_index])
    # calculate output and input power

    power_fft_output = np.sum(np.square(output_fft_around_index))
    power_input = (np.square(input_amplitude))/2

    # |H(s)|:
    magnitude_response = power_fft_output/power_input

    return magnitude_response
def calculate_magnitude_response_b(input_fft, output_fft, indices):
    """ Calculate magnitude response by capturing all power around index
        input_fft and output_fft contains multiple freq components
        Returen for each frequency component the magnitude response
    """
    n_samples_around_index = 2

    transfer_magnitude = []
    # For each index
    for i, index in enumerate(indices):
        # Define lower and upper index
        upper_index = int(index + n_samples_around_index)
        lower_index = int(index - n_samples_around_index)
    
        # Get absolute values around peak
        values_around_peak_in = np.abs(input_fft[lower_index:upper_index])
        values_around_peak_out = np.abs(output_fft[lower_index:upper_index])

        # Get power sum[|X|**2] and sum[|Y|**2]
        power_in = np.sum(values_around_peak_in**2)
        power_out = np.sum(values_around_peak_out**2)
    
        # |H| = power_out/power_in
        transfer_magnitude.append(power_out/power_in)

    return transfer_magnitude


def calculate_frequency_response(input_fft, output_fft, indices):
    """ Calculate magnitude and phase response.
        From complex fft's obtain transfer.
    """
    phase = []
    phase_test = []
    for i, index in enumerate(indices):
        transfer = output_fft[int(index)]/input_fft[int(index)]
        phase_test.append(np.arctan(np.imag(transfer)/np.real(transfer)))
        phase.append(np.angle(transfer))

    # print("phase test rad", phase_test)
    # print("phase rad",phase)

    return phase
        
def get_normalized_singlesided_fft(windowed_signal):
    """ FFT -> normalize -> rightsided"""
    signal_fft = fft(windowed_signal)
    signal_fft_normalized = signal_fft/len(signal_fft)
    signal_fft_normalized_r = signal_fft_normalized[0:len(signal_fft_normalized)//2]
    return signal_fft_normalized_r

def generate_input_time_signal(frequencies, amplitudes, sample_rate, duration):
    """ Output is a combination of discrete sine waves with
        multiple frequency components
    """
    # Define time axis
    time_axis = np.linspace(0, duration, round(sample_rate * duration), endpoint=False)

    # Time signal
    signal = np.zeros_like(time_axis)
    for frequency, amplitude in zip(frequencies, amplitudes):
        signal += amplitude*np.sin(2*np.pi*frequency*time_axis)
    
    return time_axis, signal

def sync_on_ID(data_bits, n_bytes, n_bits):
    """ SYnc on ID by looking for ID in the data bin
        If found, store the data with ID as first byte
    """
    # package length is 2 bytes
    package_length = 2*8
    for i in range(2*n_bytes):
        # Check each 2 byte on package ID
        message_type = data_bits[package_length*i: package_length*i + 2]
        # Check for each 2 bytes the message type
        if message_type == BitArray("0b01"):
            print("Synced Successfully")
            return data_bits[package_length*i: package_length*1 + n_bits]
    # If ID not found     
    print("Sync Failed")
    return BitArray(0,n_bits)

def get_freq_bin_number(frequencies_list, start_freq, stop_freq, n_bins):
    """  Expects list as input
    Get bin number where this data should be stored"""
    freq_range = stop_freq-start_freq
    difference = [frequency - start_freq for frequency in frequencies_list]
    product = np.multiply(n_bins,(difference))
    # print(np.multiply(n_bins,(difference)))
    bin_numbers = np.divide(product,freq_range)
    return list(map(int, bin_numbers))

# print(get_freq_bin_number([1.61e6], 1.58e6, 1.68e6, 100))
# print(message_to_float(BitArray('0b11010100110000')))