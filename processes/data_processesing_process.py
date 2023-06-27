""" Process of data processing"""

import numpy as np
import multiprocessing
import queue
import threading
import time
import itertools
from scipy import signal, fft

from data_processing_functions import *
from read_datastream_functions import *

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

# Headers
headers = {
    "position": 0b00,
    "ID": 0b01,
    "second_feature1": 0b10,
    "second_feature2": 0b11
}

def get_data_thread_target(data_to_process_rx, start_data_extraction,
                           trigger_calculate_fft, trigger_get_input_phasor, n_packages):
    """ Thread for getting input and output data that is used by processing"""
    # Process globals
    global system_output_data

    n_bytes = int(2*n_packages)
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

        # Get bytes from pipe containing two times bin size including headers
        bytes_from_datastream_local = data_to_process_rx.recv()
        # print("IN DATA PROCESSING", bytes_from_datastream_local)
        # Get the system output data from the pipe, this contains ID, sec feature and time samples
        # system_output_data_local = data_to_process_rx.recv()
        
        # sync on ID
        for i in range(n_bytes):
            single_byte = bytes_from_datastream_local[i]
            header_bits = (single_byte >> 6) & 0b11
            if header_bits == headers["ID"]:
                # Store the bytes corresponding to one bin
                bytes_synced = bytes_from_datastream_local[i:n_bytes+1]
                # Then break from loop
                print("ID FOUND")
                break
                
            # print("SYNCING", single_byte, header_bits)
        
        # Extract and store in a list [ID, extraFeature1, extraFeature2, pos, pos, pos ....]
        ID = bytes_synced[0:2]
        extra_feature1 = bytes_synced[2:4]
        extra_feature2 = bytes_synced[4:6]
        position = bytes_synced[6:]
        
        # Extract content
        ID_combined = (ID[0] << 8) | ID[1]
        ID_content = ID_combined & 0x3FFF # 0011 1111 1111 1111

        extra_feature1_content = extra_feature1[1]
        # extra_feature1_content = extra_feature1_combined & 0x3FFF
        
        extra_feature2_content = extra_feature2[1]
        # extra_feature2_content = extra_feature2_combined & 0x3FFF

        # extra feature is 16 bits
        extra_feature_content = (extra_feature1_content << 8) | extra_feature2_content

        n_other_bytes = 6
        # print("LENGTHS", n_bytes - n_other_bytes, len(position), len(bytes_synced))
        position_combined = [(position[0 + i] << 8) | position[1 + i] for i in range((n_bytes - n_other_bytes)//2)]
        position_content = [position_combined[i] & 0x3FFF for i in range((n_bytes - n_other_bytes)//2)]

        # Convert single point content to decimals
        # Just store id as bytes, no conversion needed
        ID_decimals = ID_content
        extra_feature_decimals = hex_to_float(extra_feature_content, size=16)
        position_decimals = [unsigned_to_decimal(sample) for sample in position_content]

        # print("non converted shit", ID_content, extra_feature_content,position_content)
        # print("Converted shit", ID_decimals, extra_feature_decimals, position_decimals)
        system_output_data_local = bytes_from_datastream_local

        # Store it to global proces mem
        with system_output_data_lock:
            # system_output_data = system_output_data_local.copy()
            
            system_output_data = [ID_decimals, extra_feature_decimals, position_decimals]
            # print("SHAPE DATA", system_output_data, np.shape(system_output_data))
        
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
            output_time_data = system_output_data[2].copy()

        # while True:
        # print("Before window",np.shape(output_time_data[0]))
        # print("OUTPUT TIME DATA")
            # time.sleep(5)

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
                                   bin_size, sample_rate, current_id_tx, bandwidth):
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
        
        # Send current ID to control process:
        current_id_tx.send(current_id)

        # Get model params from model params memory
        with model_params_lock:
            # look in first column for id
            current_model_params_index = np.where(model_params_memory[:,0]==current_id)[0]
            # print("CURRENT INDEX", current_model_params_index)
            # Extract current row
            current_model_params_id = model_params_memory[current_model_params_index,:].copy()
            # print("CUrrent params", current_model_params_id)
        print("CURRENT ID", current_id)
        # Get current input from input-register memory
        with input_register_lock:
            # look in first column for id
            current_input_register_index = np.where(input_register_memory[:,0]==current_id)[0]
            # Extract current row
            current_input = input_register_memory[current_input_register_index,:].copy()
       
        print("CURRENT INPUT", current_input_register_index,current_input)

        # Get rid of first axis
        current_input = current_input[0,:].copy()
        current_model_params_id = current_model_params_id[0,:].copy()

        # Get params, remove ID
        current_model_params = current_model_params_id[1:].copy()

        # Get frequencies and amplitudes and make global
        with input_amp_freq_lock:
            input_frequencies_global = current_input[1:5].copy()
            input_amplitudes_global = current_input[5:].copy()

            frequencies = input_frequencies_global.copy()
            amplitudes = input_amplitudes_global.copy()

        # Normalize frequencies and create vector [1,f_norm, f_norm^2 ... f_norm^7]
        frequencies_vector_normalized = []
        for frequency in frequencies:
            frequencies_vector_normalized.append(create_feature_vector_normalized(frequency,bandwidth))

        # Create system input magnitudes --> store in list
        model_magnitude_list = []
  
        # TODO: add second feature
        power_vector_normalized = [1,0,0,0,0,0,0,0]

        # Calculate X_hat (magnitude that is on the ultrasound input)
        X_hat_list = []
        for i, frequency_vector in enumerate(frequencies_vector_normalized):
            # multiply each element of power to the frequencies array
            # print("FREQ vector", frequency_vector)
            product_list = [[power_element*frequency_element for frequency_element in frequency_vector]for power_element in power_vector_normalized]
            flattened_product_list = list(itertools.chain(*product_list))

            # weights*product list (as dot operation) should result in scalar
            product_arr = np.array(flattened_product_list)
            # print("SIZES", product_arr.shape, np.shape(product_list), product_list)
            abs_H = np.dot(current_model_params, product_arr)

            X_hat_list.append(amplitudes[i]/abs_H)
            
        print("X_hats and amplitudes", X_hat_list, amplitudes)
        # amplitude/modelmag = |X|/|H|
        # system_input_magnitude = [amplitudes[i]/model_magnitude_list[i] for i in range(len(amplitudes))]
        print("INPUT MAG", X_hat_list)

        # make it global (accesable for magnitude response)
        with input_magnitude_lock:
            input_magnitude = X_hat_list

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
        # All fft variables are from process globals
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
                                   bin_size, sample_rate, magnitude_samples_tx,
                                   current_id_tx, second_feature_memory,
                                   second_feature_lock, bandwidth, n_packages):
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
              trigger_calculate_fft, trigger_get_input_phasor,
              n_packages)
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
              bin_size, sample_rate,current_id_tx,bandwidth)
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
