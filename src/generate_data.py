"""Generate data. Sweep over frequency range ()"""
import numpy as np

from random_plant import* 

#------------ frequency sweep ------------#
def frequency_sweep(start, stop, sample_rate, duration, n_sweeps):
    "Sweep over frequency"
    # Get sweep setp_size :
    step_size = int((stop-start)/n_sweeps)
    # duration = n_samples/sample_rate
    n_samples = int(duration*sample_rate)
    print("n_samples:", n_samples)
    sweeped_data_out = np.empty((n_sweeps,n_samples))
    sweeped_data_in = np.empty((n_sweeps,n_samples))
    i = 0
    print("Range : ", range(start,stop,step_size))
    for frequency in range(start, stop, step_size):
        # For each frequency generate a singal sequence and store in sweeped
        data_in, time_axis, data_out = generate_data(frequency, sample_rate, duration)
        # Make sure index inside bounds (step_size)
        if i < step_size:
            sweeped_data_out[i, :] = data_out
            sweeped_data_in[i, :] = data_in
        i += 1
    return sweeped_data_in, sweeped_data_out, time_axis

def max_amplitude_index(data):
    """Get index of max amplitude"""
    val_max = np.max(data)
    index_max = np.where(val_max==data)
    return index_max

def fft_to_singlesided(omega, fft_in, sample_rate, duration):
    """Convert double sided fft to signlesided"""
    fft_singlesided = np.empty((fft_in.shape))
    omega_singlesided = np.empty((omega.shape))
    index_mid = int(sample_rate*duration/2)
    index_end = int(sample_rate*duration)
    omega_singlesided = np.append(0,[omega[0:index_mid - 1]])
    fft_singlesided = np.append(0,[fft_in[0:index_mid - 1]])

    return omega_singlesided, fft_singlesided

def get_max_index(extra, stop_freq, omega):
    """Get maximum index for good plot resolution"""
    index = omega.size*(stop_freq+extra)/omega[omega.size-1]
    return int(index)