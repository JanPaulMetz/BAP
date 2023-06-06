""" Process of data processing"""

import numpy as np
import multiprocessing
import queue
import threading
import time
from scipy import signal, fft

from data_processing_functions import *

# Process globals
system_output_data_lock = threading.Lock()
system_output_data = []

input_magnitude_lock = threading.Lock()
input_magnitude = []

frequency_fft_indices_lock = threading.Lock()
frequency_fft_indices = []

fft_lock = threading.Lock()
fft_result = []
fft_omega = []

input_amp_freq_lock = threading.Lock()
input_frequencies_global = []
input_amplitudes_global = []

magnitude_response_lock = threading.Lock()
magnitude_response_global = []

def get_data_thread_target(data_to_process_rx, start_data_extraction,
                           trigger_calculate_fft, trigger_get_input_phasor):
    """ Thread for getting input and output data that is used by processing"""
    # Process globals
    global system_output_data

    while True:
        # Wait for storing thread to be ready
        start_data_extraction.wait()
        # Wait for data to appear in the pipe
        while not data_to_process_rx.poll():
            print("Waiting to receive data to process")
            time.sleep(0.1)
        print("Received data to process")

        # Clear extraction flag, meaning that dataprocessing is happening
        start_data_extraction.clear()

        # Get the system output data from the pipe, this contains ID, sec feature and time samples
        system_output_data_local = data_to_process_rx.recv()

        # Store it to global proces mem
        with system_output_data_lock:
            system_output_data = system_output_data_local.copy()
        
        # Trigger calculate fft thread
        trigger_calculate_fft.set()

        # Trigger get_input_phasor_thread
        trigger_get_input_phasor.set()

def calculate_fft_thread_target(trigger_calculate_fft,calculate_fft_ready, bin_size, sample_rate):
    """ Thread that gets fft of output signal """
    global system_output_data
    global fft_omega
    global fft_result
    while True:
        # Wait for start
        trigger_calculate_fft.wait()

        # Reset
        trigger_calculate_fft.clear()

        # Get time data (So without ID and Temp sample)
        with system_output_data_lock:
            output_time_data = system_output_data[2:].copy()
        
        # Get hann window and multiply with time signal
        hann_window = signal.windows.hann(int(bin_size))
        windowed_output = output_time_data*hann_window

        # Perfom FFT on windowed time signal (normalized to size and compensated for hann window (1.63))
        fft_size = bin_size//2
        output_fft = 1.63*fft.rfft(windowed_output)/fft_size
        omega_fft = fft.rfftfreq(windowed_output.size, 1/sample_rate)
        
        # Make global
        with fft_lock:
            fft_result = output_fft.copy()
            fft_omega = omega_fft.copy()
        
        # Finished
        calculate_fft_ready.set()

def get_input_phasor_thread_target(model_params_memory, model_params_lock,
                                   input_register_memory, input_register_lock,
                                   trigger_get_input_phasor, get_input_phasor_ready,
                                   bin_size, sample_rate):
    """ Thread that gets the input phasor that is used to drive the system
        system_input_magnitude = w.T*phi(f)
        where w is the model weight vector, obtained from model params memory
        where phi(f) = [1, f, f**2, f**3 ..., f**9] --> called frequency_vector
    """
    # Process globals
    global system_output_data
    global input_magnitude
    global frequency_fft_indices
    global input_amplitudes_global
    global input_frequencies_global

    while True:
        # Wait for start sign
        trigger_get_input_phasor.wait()
        # Reset
        trigger_get_input_phasor.clear()
        # Get current ID
        with system_output_data_lock:
            current_id = system_output_data[0]

        # Get model params from model params memory
        with model_params_lock:
            # look in first column for id
            current_model_params_index = np.where(model_params_memory[:,0]==current_id)[0]
            # print("CURRENT INDEX", current_model_params_index)
            # Extract current row
            current_model_params_id = model_params_memory[current_model_params_index,:].copy()
            # print("CUrrent params", current_model_params_id)

        # Get current input from input register memory
        with input_register_lock:
            # look in first column for id
            current_input_register_index = np.where(input_register_memory[:,0]==current_id)[0]
            # Extract current row
            current_input = input_register_memory[current_input_register_index,:].copy()

        # Get rid of first axis
        current_input = current_input[0,:].copy()
        current_model_params_id = current_model_params_id[0,:].copy()

        # Get params, remove ID
        current_model_params = current_model_params_id[1:].copy()

        # Get frequencies and amplitudes and make global
        with input_amp_freq_lock:
            input_frequencies_global = current_input[1:4].copy()
            input_amplitudes_global = current_input[4:].copy()

            frequencies = input_frequencies_global.copy()
            amplitudes = input_amplitudes_global.copy()

        # Create system input magnitudes --> store in list
        model_magnitude_list = []
  
        for frequency in frequencies:
            # Create frequency polynomials
            frequency_vector = create_frequency_vector(frequency)
            # Get model magnitude for this frequency
            model_magnitude = np.dot(current_model_params, frequency_vector)
            # Append
            model_magnitude_list.append(model_magnitude)

        print("Model mags", model_magnitude_list, amplitudes)
        # amplitude/modelmag = |X|/|H|
        system_input_magnitude = [amplitudes[i]/model_magnitude_list[i] for i in range(len(amplitudes))]
        print("INPUT MAG", system_input_magnitude)

        # make it global (accesable for magnitude response)
        with input_magnitude_lock:
            input_magnitude = system_input_magnitude

        # Get fft indices of each frequency component
        fft_indices = []
        for frequency in frequencies:
            fft_indices.append(get_fft_index(frequency, sample_rate, bin_size))
        
        # Make global accessible for threads
        with frequency_fft_indices_lock:
            frequency_fft_indices = fft_indices.copy()

        get_input_phasor_ready.set()

def calculate_magnitude_response_thread_target(get_input_phasor_ready, calculate_fft_ready, calculate_magnitude_ready):
    """ Thread that calculates magnitude response for given data (freq component)"""
    global fft_result
    global fft_omega
    global frequency_fft_indices
    global input_magnitude
    global input_amplitudes_global
    global input_frequencies_global
    global magnitude_response_global

    n_around_freq = 4

    while True:
        # Wait for both getinputphasor and fft threads to be ready:
        get_input_phasor_ready.wait()
        calculate_fft_ready.wait()

        # Reset
        get_input_phasor_ready.clear()
        calculate_fft_ready.clear()

        print("CALCULATE MAG")

        # Get power around each frequency component from output fft
        with fft_lock:
            output_fft = fft_result
            omega = fft_omega

        with frequency_fft_indices_lock:
            fft_indices = frequency_fft_indices.copy()
        
        with input_amp_freq_lock:
            input_amplitudes = input_amplitudes_global.copy()
            input_frequencies = input_frequencies_global.copy()

        with input_magnitude_lock:
            input_magnitudes = input_magnitude.copy()
        # Capture power around peaks
        power_out_list = []
        for i, frequency in enumerate(input_frequencies):
            # Get upper and lower index
            upper_index = int(fft_indices[i] + n_around_freq)
            lower_index = int(fft_indices[i] - n_around_freq)

            # Get magnitudes around peak (freq component)
            magnitudes_around_peak = np.abs(output_fft[lower_index:upper_index])

            # Append power--? P = sum(magnitudes**2) = |X(f)|**2
            power_out_list.append(np.sum(magnitudes_around_peak**2))
        
        # Get power from input P = |X_hat|**2
        power_in_list = [magnitude**2 for magnitude in input_magnitudes]

        # Calculate magnitude response per frequency |H| = |Y|/|X| = |Y(f)|**2/|X(f)|**2
        magnitude_response = [power_out/power_in for power_out, power_in in zip(power_out_list,power_in_list)]

        print("MAGNITUDE RESPONSE",magnitude_response, power_in_list, power_out_list)

        with magnitude_response_lock:
            magnitude_response_global = magnitude_response.copy()
        calculate_magnitude_ready.set()

def store_samples_thread_target(calculate_magnitude_ready, start_data_extraction, magnitude_samples_tx):
    """ Thread for storing samples that are calculated (phase and mag)
        Also triggers data extraction
    """
    global magnitude_response_global
    global input_frequencies_global

    while True:
        calculate_magnitude_ready.wait()
        calculate_magnitude_ready.clear()

        print("STORING SAMPLES")
        # Get magnitude response
        with magnitude_response_lock:
            magnitude_response = magnitude_response_global.copy()
        
        # Get Temp
        with system_output_data_lock:
            temperature = system_output_data[1]

        # Get frequencies
        with input_amp_freq_lock:
            frequencies = input_frequencies_global.copy()

        # Load in one list |freqs|temp|magnitude response|
        temperature = [temperature] # For concatenating it in list
        list_to_send = frequencies.tolist() + temperature + magnitude_response

        print("LIST TO SEND", list_to_send)
        
        # Send magnitude samples to the data training process
        magnitude_samples_tx.send(list_to_send)

        start_data_extraction.set()

def data_processing_process_target(data_to_process_rx, start_data_extraction,   # data to process connection
                                   model_params_memory, model_params_lock,       # model params memory
                                   input_register_memory, input_register_lock, # input register memory
                                   bin_size, sample_rate, magnitude_samples_tx):
    """ Target function for multiprocessing process"""
# Flags (triggers)
    trigger_calculate_fft = threading.Event()
    trigger_get_input_phasor = threading.Event()
    calculate_fft_ready = threading.Event()
    get_input_phasor_ready = threading.Event()
    calculate_magnitude_ready= threading.Event()

# Create Threads

    # Get data
    get_data_thread = threading.Thread(
        target=get_data_thread_target,
        args=(data_to_process_rx, start_data_extraction,
              trigger_calculate_fft, trigger_get_input_phasor)
    )
    # Calculate FFT
    calculate_fft_thread = threading.Thread(
        target=calculate_fft_thread_target,
        args=(trigger_calculate_fft,calculate_fft_ready, bin_size, sample_rate)
    )
    # Get input phasor
    get_input_phasor_thread = threading.Thread(
        target=get_input_phasor_thread_target,
        args=(model_params_memory, model_params_lock,
              input_register_memory, input_register_lock,
              trigger_get_input_phasor, get_input_phasor_ready,
              bin_size, sample_rate)
    )
    # Calculate magnitude response
    calculate_magnitude_response_thread = threading.Thread(
        target=calculate_magnitude_response_thread_target,
        args=(get_input_phasor_ready, calculate_fft_ready, calculate_magnitude_ready)
    )
    # Store samples
    store_samples_thread = threading.Thread(
        target=store_samples_thread_target,
        args=(calculate_magnitude_ready, start_data_extraction,
              magnitude_samples_tx)
    )

# Start threads
    get_data_thread.start()
    calculate_fft_thread.start()
    get_input_phasor_thread.start()
    calculate_magnitude_response_thread.start()
    store_samples_thread.start()

    while True:
        time.sleep(1)
