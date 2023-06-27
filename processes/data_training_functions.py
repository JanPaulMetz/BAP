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

def normalize_frequency(frequency):
    """ Normalizes frequency to decrease product number size"""
    f_min = 1
    f_max = (1.525e6)^7
    frequency_normalized = 0.725*(1.275 + ((frequency - (f_min + f_max)/2) / ((f_max - f_min)/2)))
    return frequency_normalized

def normalize_second_feature(feature):
    """ Normalize second feature """
    feature_min = 0
    feature_max = 1
    feature_normalized = 0.725*(1.275 + ((feature - (feature_min + feature_max)/2) / ((feature_max - feature_min)/2)))
    return feature_normalized