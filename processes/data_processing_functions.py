""" Functions used in data_processing process"""
import numpy as np

def get_system_input_phasor(input_magnitude, model_magnitude):
    """ Flat response if input values H^-1 = (1/|H|)
        So driven with input magnitude results in 
        X_hat = inputmagnitude*(1/model_magnitude) = X*H^-1
        X_hat will be the true input of the system
        """
    # Devision by 0 will raise error
    if model_magnitude==0:
        return None
    else:
        system_magnitude = input_magnitude/model_magnitude
    return system_magnitude

def create_frequency_vector(frequency):
    """ Creates frequency vector 
        phi(f) = [1, f, f^2, f^3 ...].T (size = 10)
    """
    size = 10
    frequency_vector = np.zeros(size)
    for i in range(size):
        frequency_vector[i] = frequency**i

    return frequency_vector

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
