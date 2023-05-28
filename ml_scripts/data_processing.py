""" Module containing functions used by the data_processing() thread
    1. message_to_float
    2. 

"""

import numpy as np
from bitstring import BitArray
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

def get_fft_index(frequency, sample_rate, bin_size):
    """ Get index at which this frequency component is placed 
        after performing a DTFT
    """
    # Calculate frequency spacing
    delta_f = sample_rate/bin_size
    # Calculate the bin_number (is the index)
    bin_number = np.round(frequency/delta_f)

    return bin_number


def calculate_magnitude_response(output_fft_normalized, input_amplitude, index):
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

def calculate_frequency_response(ID, temperature, time_in, time_out, sample_rate, bin_size):
    """ Calculate magnitude and phase response.

        Input: ID, Temperature, input_time_data, output_time_data, 
        system sample rate, size of time bin

        Output: trigger training. Store freq data in master bin
    """
    #
    print('empty')

def pop_old_input_data():
    """ Pop all data older than current ID"""
    print("pop")

# print(message_to_float(BitArray('0b11010100110000')))