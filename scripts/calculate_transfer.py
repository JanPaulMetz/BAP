"""This module calculates transfer function using input and output"""
import numpy as np
from scipy import signal 

def calculate_transfer_magnitude(input_fft, output_fft):
    """Calculates transfer magnitude |H(s)| = |Y(s)|/|X(s)| numeric of 1 sample"""
    # Get indeces of input_fft where nonzero
    nonzero_indices = [index for index, value in enumerate(input_fft) if value>0.01]

    # Input and output of type np array
    nonzero_transfer_function = np.divide(output_fft[nonzero_indices], input_fft[nonzero_indices])
    transfer_function = np.zeros(np.shape(input_fft))

    j_max = nonzero_transfer_function.size
    i = 0
    j = 0
    # Fil in nonzero values in transferfunction
    while j<j_max:
        if i == nonzero_indices[j]:
            # print("j", j)
            transfer_function[i] = nonzero_transfer_function[j] 
            # increment j if index is taken
            j += 1
        # increment i every loop
        i += 1
    # Only return left half (n_samples/2),
    # since right half is mirrored image
    n_samples = 0.5*input_fft.size
    return transfer_function[0:int(n_samples)]

#TODO: CHECK FOR OUTLIERS
def mean_transfer(transfer_matrix):
    """Take mean of all non-zero values per column"""
    mean_transfer_list = []
    print("SHAPE t matrix", transfer_matrix.shape)
    for i in range(transfer_matrix.shape[1]): # For all columns 
        # Copy nonzero row
        nonzeros_row = transfer_matrix[transfer_matrix[:,i] > 0] # Store all nonzeros
        # Get nonzero terms
        nonzeros = nonzeros_row[nonzeros_row > 0]
        # if empty slice:
        if len(nonzeros) == 0:
            nonzeros = 0
        # MAYBE CHECK FOR OUTLIERS?
        nonzeros_mean = np.mean(nonzeros)
        mean_transfer_list.append(nonzeros_mean)

    mean_transfer_array = np.array(mean_transfer_list)
    # Get zero indeces
    # zero_ind = np.empty((mean_transfer_array.size),1)
    nonzero_ind = np.where(mean_transfer_array > 0)
    # print(zero_ind)
    return mean_transfer_array, nonzero_ind
