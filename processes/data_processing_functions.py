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

def normalize_old(feature, range):
        """ Function that is normalizing"""
        return 1.275 + (1.25 + (feature - (range[0] + range[1])/2) / ((range[1] - range[0])/2))

def normalize(feature, range):
     return 0.725*((feature- (range[0] + range[1])/2 )/((range[1]-range[0])/2) + 1.275)

def create_feature_vector_normalized(feature, feature_range):
    """ Creates frequency vector 
        phi(f) = [1, f, f^2, f^3 ..., f^7].T (size = 10)
    """
    size = 8
    # feature_vector = np.zeros(size)
    feature_normalized = normalize(feature, feature_range)
    feature_vector_normalized = [feature_normalized**i for i in range(size)]

    # feature_vector = [feature**i for i in range(size)]
    # feature_vector_normalized = [normalize(feature, feature_range) for feature in feature_vector]

    # for i in range(size):
    #     feature_vector[i] = feature**i

    return feature_vector_normalized

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


# print(create_feature_vector_normalized(1.6e6, [1.575e6, 1.625e6]))
