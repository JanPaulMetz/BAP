""" Implementation of data training process """

import numpy as np
import multiprocessing
import threading
import time
from collections import deque

from data_training_functions import *

# Max deque size
max_frequency_bin_size = 10

# Number of frequency bins
n_frequency_bins = 100

# Number of temperature bins
n_temperature_bins = 50

# Magnitude samples are stored in (process) global list 
# magnitude_samples[freq_bin][temp_bin]
magnitude_samples_lock = threading.Lock()
magnitude_samples = [[deque(maxlen=max_frequency_bin_size) for _ in range(n_temperature_bins)] for _ in range(n_frequency_bins)]

# Flags
start_training = threading.Event()

# Model parameters
model_parameters_lock = threading.Lock()
model_parameters = []

def sample_manager_thread_target(magnitude_samples_rx, bandwidth):
    """ Updates bin containing all magnitude samples 
        Samples are stored in deque, that is automatically throwing
        away samples if maximum needed (oldest samples)
    """
    global magnitude_samples
    new_sample_count = 0
    train_after_n_samples = 10

    while True:
        # Block untill new samples are received
        while not magnitude_samples_rx.poll():
            # print("waiting for magnitude samples")
            time.sleep(0.1)
        
        # Receive samples |Freq1|Freq2|Freq3|temperature|magnitude1|magnitude2|magnitude3|
        new_magnitude_samples = magnitude_samples_rx.recv()
        print("SHAPE", np.shape(new_magnitude_samples))
        # Extract frequencies
        frequencies = new_magnitude_samples[0:2].copy()

        print("SIZE temp", np.shape(new_magnitude_samples))
        # Ectract temperature
        temperature = new_magnitude_samples[3]

        # Extract magnitudes
        magnitude_responses = new_magnitude_samples[4:]

        # Determine frequency bins
        frequency_bin_numbers = get_freq_bin_number(frequencies, bandwidth, n_frequency_bins)

        # Determine temperature bin (same method as freqs, but for now constant)
        temperature_bin_number = 0

        # Store data in the corresponding bin (Right freq and temp bin)
        # Data is stored as (freq,temperature,magnitude)
        with magnitude_samples_lock:
            for i, frequency_bin_number in enumerate(frequency_bin_numbers):
                print(frequencies[i])
                print(temperature)
                print(magnitude_responses[i])
                magnitude_samples[frequency_bin_number][temperature_bin_number].appendleft((frequencies[i],temperature,magnitude_responses[i]))

        # Count new samples
        new_sample_count += 1
        # print("SAMPLE COUNT", new_sample_count)
        # After n new samples, start training
        if new_sample_count >= train_after_n_samples:
            # Reset new sample count
            new_sample_count = 0
            # Trigger training thread
            start_training.set()


def train_magnitude_thread_target(new_model_parameters_tx, frequency_plot_tx,
                                  temperature_plot_tx,magnitude_plot_tx, magnitude_data_updated):
    """ Train the data bin"""
    global magnitude_samples
    global model_parameters
    while True:
        # Wait on training trigger
        start_training.wait()
        start_training.clear()

        # Start training (for now 2D, linear response)
        with magnitude_samples_lock:
            samples_to_fit = magnitude_samples.copy()
        
        # For now, extract the frequency axis for temperature bin 0
        temperature_bin = 0
        frequency_axis = [temperature[temperature_bin] for temperature in samples_to_fit]
        
        # Unpack frequency_axis, so get all data points
        # [(freq, temp, mag),(freq, temp, mag),(freq, temp, mag) ....]
        samples_unpacked = []
        [samples_unpacked.extend(element) for element in frequency_axis]

        # Get freq and temp as array
        frequency, temperature, magnitude = zip(*samples_unpacked)

        # put in array
        frequency = np.array(frequency)
        temperature = np.array(temperature)
        magnitude = np.array(magnitude)
        
        # Send sampels to plotter
        frequency_plot_tx.send(frequency)
        temperature_plot_tx.send(temperature)
        magnitude_plot_tx.send(magnitude)
        # Set flag that is telling the data is in the pipe
        magnitude_data_updated.set()

        # Start fitting the unpacked data
        magnitude_fit = np.polyfit(frequency, magnitude, deg=9)

        # magnitude_fit contains parameters but reversed convention
        model_params = magnitude_fit[::-1]

        # Pipe to main
        print("MODEL PARAMS", model_params)
        new_model_parameters_tx.send(model_params)


def data_training_process_target(magnitude_samples_rx, bandwidth, new_model_parameters_tx,
                                 frequency_plot_tx, temperature_plot_tx,magnitude_plot_tx, magnitude_data_updated):
    """ Target for process data training"""
# Create Threads
    # Sample manager
    sample_manager_thread = threading.Thread(
        target=sample_manager_thread_target,
        args=(magnitude_samples_rx,bandwidth)
    )
    # Train Magnitude
    train_magnitude_thread = threading.Thread(
        target=train_magnitude_thread_target,
        args=(new_model_parameters_tx,frequency_plot_tx,
              temperature_plot_tx,magnitude_plot_tx, magnitude_data_updated)
    )

# Start Threads
    sample_manager_thread.start()
    train_magnitude_thread.start()

    while True:
        time.sleep(1)
