""" Functions used by data training process """
import numpy as np

def get_freq_bin_number(frequencies_list, bandwidth, n_bins):
    """  Expects list as input
    Get bin number where this data should be stored"""
    # Get range
    min_freq = bandwidth[0]
    max_freq = bandwidth[1]
    freq_range = max_freq - min_freq

    # Get differences between frequency and min frequency
    difference = [frequency - min_freq for frequency in frequencies_list]
    product = np.multiply(n_bins,(difference))
    bin_numbers = np.divide(product,freq_range)

    # Return bin number as integers (round down)
    return list(map(int, bin_numbers))