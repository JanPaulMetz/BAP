""" Process of data processing"""

import numpy as np
import multiprocessing
import queue
import threading
import time

def test_thread_target(data_to_process_rx,start_data_extraction):
    """testing queue""" 
    while True:
        start_data_extraction.set()
        while not data_to_process_rx.poll():
            print("NOT receiving")
            time.sleep(1)
        print("REceiving")
        # Clear extraction flag
        start_data_extraction.clear()
        # Receive data
        data_to_process = data_to_process_rx.recv()
        print("REceived data", data_to_process)

def get_data_thread_target(data_to_process_rx, start_data_extraction, model_params_memory, model_params_lock):
    """ Thread for getting input and output data that is used by processing"""
    while True:
        # Wait for data to appear in the pipe
        while not data_to_process_rx.poll():
            print("Waiting to receive data to process")
            time.sleep(0.1)
        # print("Received data to process")

        # Clear extraction flag, meaning that dataprocessing is happening
        start_data_extraction.clear()

        # Get the system output data from the pipe, this contains ID, sec feature and time samples
        system_output_data = data_to_process_rx.copy()

        # Get current ID
        current_id = system_output_data[0]
        print("CURRENT ID")
        # Collect model params
        with model_params_lock:
            current_id_index = np.where(model_params_memory[:,0]==current_id)
        print("CURRENT INDEX", current_id_index)

def calculate_fft_thread_target():
    """ Thread that gets fft of output signal """
    print("test")

def get_input_phasor_thread_target():
    """ Thread that gets the input phasor that is used to drive the system """
    print("test")

def calculate_magnitude_response_thread_target():
    """ Thread that calculates magnitude response for given data (freq component)"""
    print("test")

def calculate_phase_response_thread_target():
    """ Thread that calculates phase response for given data (freq component) """
    print("test")

def store_samples_thread_target():
    """ Thread for storing samples that are calculated (phase and mag)
        Also triggers data extraction
    """
    print("test")

def data_processing_process_target(data_to_process_rx, start_data_extraction, model_params_memory, model_params_lock):
    """ Target function for multiprocessing process"""


    test_thread = threading.Thread(
        target=test_thread_target,
        args=(data_to_process_rx,start_data_extraction)
    )
    test_thread.start()
# Create Threads
    get_data_thread = multiprocessing.Process(
        target=get_data_thread_target,
        args=(data_to_process_rx, start_data_extraction,
              model_params_memory, model_params_lock)
    )
    calculate_fft_thread = multiprocessing.Process(
        target=calculate_fft_thread_target,
        args=()
    )
    get_input_phasor_thread = multiprocessing.Process(
        target=get_input_phasor_thread_target,
        args=()
    )
    calculate_magnitude_response_thread = multiprocessing.Process(
        target=calculate_magnitude_response_thread_target,
        args=()
    )
    calculate_phase_response_thread = multiprocessing.Process(
        target=calculate_phase_response_thread_target,
        args=()
    )
    store_samples_thread = multiprocessing.Process(
        target=store_samples_thread_target,
        args=()
    )

# Start threads
    get_data_thread.start()
    calculate_fft_thread.start()
    get_input_phasor_thread.start()
    calculate_magnitude_response_thread.start()
    calculate_phase_response_thread.start()
    store_samples_thread.start()

    while True:
        time.sleep(1)
