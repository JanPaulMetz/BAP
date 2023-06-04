""" Toplevel script containing threads"""
from time import sleep
import time
import itertools
import threading
import queue
import serial

from scipy.fft import fft, fftfreq
from scipy import signal
import numpy as np
import pandas as pd

from bitstring import BitArray
from collections import deque

from data_processing import *
from generate_data import generate_discrete_sine
# ESP32
esp_baud_rate = 115200
esp_port = 'COM10'

# Data stream serial
stream_baud_rate= 115200
stream_port = 'COM11'

# Data stream
n_packages = int(80)
n_bytes = int(2*n_packages) # 2 bytes per package
n_bits = int(8*n_bytes)     # 8 bits per byte

# Data Processing
ready_to_process = True # used to check whether processing thread is ready
current_ID = 0
current_temperature = 0

# System constants
sample_rate = 65e6 # samples/sec
bin_size = int(n_packages - 2) # binsize of time data (in samples)
duration = bin_size/sample_rate
min_frequency = 1.58e6
max_frequency = 1.68e6

# Window
hann_window = np.copy(signal.windows.hann(int(bin_size), False))

# DataFrame containing ID's and frequency components with amplitude that are used for input
n_frequencies = 3
# ID arduino  0.4722900390625
input_df = pd.DataFrame({'ID': [-0.41168212890625], 'Frequency1':[1.589e6], 'Amplitude1':[1],'Frequency2':[1.621e6],
                          'Amplitude2':[0.3],'Frequency3':[1.66e6], 'Amplitude3':[0.57]})

# Data bins containing magnitude and phase response
total_bandwith = 100e3 # Hz
n_freq_bins = 100
max_freq_bins_length = 10
storage_bw = total_bandwith/max_freq_bins_length
magnitude_master_bin = [deque(maxlen=max_freq_bins_length) for _ in range(n_freq_bins)]
phase_master_bin = [deque(maxlen=max_freq_bins_length) for _ in range(n_freq_bins)]
# Globals that are accessed by model estimation and phase fit and magnitude fit
master_magnitude_unpacked = queue.Queue()
master_phase_unpacked = queue.Queue()

# Sweep FIFO 
sweep_fifo = queue.Queue()

# Contains all unprocessed data
data_bin = bytearray()  
# Locks            
data_lock = threading.Lock()
master_bin_lock = threading.Lock()

# Control state
control_state = "default"
# Events
stop_threads = threading.Event()        # For exiting all threads
master_ready = threading.Event()        # For accessing master
magnitude_fitted = threading.Event()    # Status of fitted
phase_fitted = threading.Event()        # Status 
transmit_instructions = threading.Event()   # Trigger for TX
frequency_sweep = threading.Event()     # Trigger for starting sweep
frequency_sweep_finished = threading.Event()   # Always in combination with frequency_sweep!!
mcu_ready = threading.Event()           # mcu ready flag--> only set once


# Conditions
start_training = threading.Condition()
start_fitting = threading.Condition()

# Mock read 
mock_data = b''
# Mock input
def control_thread():
    """ Thread for controlling the system state"""
    global control_state
    while not stop_threads.is_set():
        # wait till mcu is ready (only first loop after start)
        mcu_ready.wait()
        
        # First time freq sweep
        if mcu_ready.is_set():    
            # Activate frequency sweep
            frequency_sweep.set()
            frequency_sweep_finished.clear()
            
            # Wait till freq sweep is finsihed
            frequency_sweep_finished.wait()
            frequency_sweep_finished.clear()
        
        # Control state determined by user input
        if control_state == "default":
            # get user input frequency and amplitude
            user_input = 'TBD'
        elif control_state == "frequency_sweep":
            # Activate freq sweep thread
            frequency_sweep.set()
            frequency_sweep_finished.clear()

            frequency_sweep_finished.wait()
        else:
            # If not defined, set default
            control_state = 'default'



def mock_thread():
    """ Mocking the input data stream"""
    global mock_data
    id_byte = BitArray('0b0110010110100111')
    feature_byte = BitArray('0b1001010010110110')
    time_byte = BitArray('0b0001010001010111')

    id_byte_rev = BitArray('0b1110010110100110')
    feature_byte_rev = BitArray('0b1101010010110101')
    time_byte_rev = BitArray('0b1101010001010100')
    # byte_id = int(id_byte.to01(), 2).to_bytes(len(id_byte) // 8, byteorder='big')
    byte_id = bytes.fromhex(id_byte.hex)
    byte_feature = bytes.fromhex(feature_byte.hex)
    byte_time = bytes.fromhex(time_byte.hex)
    print(byte_id)
    # stop_threads.set()
    package_size = int(80)
    n_bytes = int(package_size//2)
    fill_mock = bytes()

    while not stop_threads.is_set():
        time_start = time.time()
        if True == True:
            for i in range(package_size):
                if i == 0:
                    fill_mock = fill_mock +byte_id
                elif i == 1:
                    fill_mock = fill_mock +byte_feature
                else:
                    fill_mock = fill_mock +byte_time
        if True == False:
            for i in range(package_size):
                if i == package_size:
                    fill_mock = fill_mock +byte_id
                elif i == package_size -1:
                    fill_mock = fill_mock +byte_id
                else:
                    fill_mock = fill_mock +byte_id
        # print("DATA RATE =", package_size/(time.time()-time_start))
        mock_data = fill_mock
        
        # mock_data.append(binascii.hexlify(fill_mock).decode('utf-8'))
        # print(mock_data)
        # stop_threads.set()



def extract_data():
    """ Thread is extracting the data 
        2 modes: sweep or user input
        If sweep        --> store in sweep queue
        It will be processed in prallel and switch back to user input
        if sweep processing is done 
    
        If user input   --> Directly process
        """
    count = 0
    while not stop_threads.is_set():
        count += 1
        start_time = time.time()
        with data_lock:
            # Get data from data_bin (twice the size for locking on the ID byte)
            data_to_process = data_bin[0:2*n_bytes].copy()
            # print("databin", data_bin)

        data_to_process_string = data_to_process.hex()
        
        # Only process non empty bins
        if data_to_process_string:
            with data_lock:
                # Clear data_bin, so that it does not overflow
                data_bin.clear()
            print("Tries to read",count)

            # Convert bytearray to bitarray
            data_to_process_bits = BitArray(data_to_process)
    
            package_length = 2*8 # 2 bytes in bits

            # Package types:
            type_time_data = BitArray('0b00')
            type_second_feature = BitArray('0b10')
            type_ID = BitArray('0b01')
            type_error = BitArray('0b11')

            # Extract databin of length n_messages (1 message is 2 bytes) starting with ID byte
            data_bits = data_to_process_bits.copy()

            # Sync on ID, extract package with length n_bits
            data_to_process_bits = sync_on_ID(data_bits, n_bytes, n_bits)
        
            # type_mes = data_to_process_bits[m/essage_length*i+2: message_length*i + 16]
            time_domain_samples_out = []
            current_ID = 0
            # For each 2 bytes (message) extract the data and convert to float
            for i in range(n_packages):

                # Two MSB's --> message type
                package_type = data_to_process_bits[package_length*i: package_length*i + 2]
                # print("Message type", message_type)

                # 14 LSB's --> message content
                package_content = data_to_process_bits[package_length*i+2: package_length*i + 16]
            
                # Time message
                if package_type == type_time_data:
                    package_float = single_point_to_decimal(package_content)

                    # Append all time domain samples to this list
                    time_domain_samples_out.append(package_float)

                # ID
                elif package_type == type_ID:
                    package_float = single_point_to_decimal(package_content)
                    current_ID = package_float
                    # print("ID", message_float)
                    
                # Temperature
                elif package_type == type_second_feature:
                    package_float = single_point_to_decimal(BitArray('0b01101010101010'))
                    current_temperature = package_float
                    # print("Temperature")
                # Error in message
                elif package_type == type_error:
                    print("Error in message")
            
            # Data is extracted, do something depending on system mode
            
            if frequency_sweep.is_set():
                
            else:
# Data processing thread
def data_processing():
    """ The intention is to use this function as a threaded function
        It calculates the magnitude and phase response of the current
        time data (for a max of 4 frequency components at a time)
        the start_processing condition is used as trigger for starting
        the processing of the time-domain data
    """
    
    count = 0
    while not stop_threads.is_set():
        """ Moved to data extracting 
        count += 1
        start_time = time.time()
        with data_lock:
            # Get data from data_bin (twice the size for locking on the ID byte)
            data_to_process = data_bin[0:2*n_bytes].copy()
            # print("databin", data_bin)

        data_to_process_string = data_to_process.hex()
        
        # Only process non empty bins
        if data_to_process_string:
            with data_lock:
                # Clear data_bin, so that it does not overflow
                data_bin.clear()
            print("Tries to read",count)
            
            # Convert bytearray to bitarray
            data_to_process_bits = BitArray(data_to_process)
    
            package_length = 2*8 # 2 bytes in bits

            # Package types:
            type_time_data = BitArray('0b00')
            type_second_feature = BitArray('0b10')
            type_ID = BitArray('0b01')
            type_error = BitArray('0b11')

            # Extract databin of length n_messages (1 message is 2 bytes) starting with ID byte
            data_bits = data_to_process_bits.copy()

            # Sync on ID, extract package with length n_bits
            data_to_process_bits = sync_on_ID(data_bits, n_bytes, n_bits)
            # print("ID",data_to_process_bits)
          
            # type_mes = data_to_process_bits[m/essage_length*i+2: message_length*i + 16]
            time_domain_samples_out = []
            current_ID = 0
            # For each 2 bytes (message) extract the data and convert to float
            for i in range(n_packages):

                # Two MSB's --> message type
                package_type = data_to_process_bits[package_length*i: package_length*i + 2]
                # print("Message type", message_type)

                # 14 LSB's --> message content
                package_content = data_to_process_bits[package_length*i+2: package_length*i + 16]
            
                # Time message
                if package_type == type_time_data:
                    package_float = single_point_to_decimal(package_content)

                    # Append all time domain samples to this list
                    time_domain_samples_out.append(package_float)

                # ID
                elif package_type == type_ID:
                    package_float = single_point_to_decimal(package_content)
                    current_ID = package_float
                    # print("ID", message_float)
                    
                # Temperature
                elif package_type == type_second_feature:
                    package_float = single_point_to_decimal(BitArray('0b01101010101010'))
                    current_temperature = package_float
                    # print("Temperature")
                # Error in message
                elif package_type == type_error:
                    print("Error in message")
            
            # Data is extracted, start getting frequency response of this data bin:
            """
            # Extract data from input_df
            print("cuurent id", current_ID)
            current_index = input_df.loc[input_df['ID']==current_ID].index[0]
            current_input = input_df.loc[current_index]
            frequencies = current_input[["Frequency1","Frequency2","Frequency3"]]
            amplitudes = current_input[["Amplitude1","Amplitude2","Amplitude3"]]

            # Generate time domain input signal
            time_axis, time_domain_samples_in = generate_input_time_signal(frequencies, amplitudes,sample_rate, duration)

            # Window time signal
            print("in",len(time_domain_samples_in))
            print("out",len(time_domain_samples_out))
            print("hann",len(hann_window))

            windowed_input = hann_window*time_domain_samples_in
            windowed_output = hann_window*time_domain_samples_out

            # Get normalized singlesided output fft
            input_fft = get_normalized_singlesided_fft(windowed_input)
            output_fft = get_normalized_singlesided_fft(windowed_output)

            # Get indices where frequency component is present
            fft_indices = get_fft_index(frequencies, sample_rate, bin_size)

            # Remove indices for which amplitude (power) = 0
            indices_to_keep = np.where(np.abs(amplitudes)>0)[0]
            print(indices_to_keep)
            fft_indices = fft_indices[indices_to_keep]

            # Get magnitude response for each frequency component
            magnitude_response = calculate_magnitude_response_b(input_fft, output_fft, fft_indices)
            
            # Get phase response for each frequency component
            phase_response = calculate_frequency_response(input_fft, output_fft, fft_indices)

            # Get frequency bin number
            freq_bin_nums = get_freq_bin_number(frequencies,min_frequency, max_frequency, n_freq_bins)

            # Wait untill master bins are ready
            print("wait on master", master_ready.is_set())
            master_ready.wait()
            # Clear, so that other threads do not access the bins
            master_ready.clear()
            # lock mster bins, those are used by other threads!
            with master_bin_lock:
                for i, bin_num in enumerate(freq_bin_nums):
                    # Append results to the master bins:
                    print(bin_num)
                    print(magnitude_response[i])
                    magnitude_master_bin[bin_num].append((frequencies[i],magnitude_response[i]))
                    phase_master_bin[bin_num].append((frequencies[i],phase_response[i]))

            # Set master_ready, so that other threads can access again
            master_ready.set()
            # Notify model estimation thread
            with start_training:
                start_training.notify()

            print(len(time_domain_samples_out))
            # data_to_process.clear()
            print("time",time.time()- start_time)
            # print("MASTER", magnitude_master_bin)
            count = 0
            
# Model estimation thread
def model_estimation():
    """ Fits a polynomial to the data that is containing the phase and 
        magnitude response.
    """
    while not stop_threads.is_set():

        # Wait with training till dataprocessing notifies
        with start_training:
            print("Waiting to be notified")
            start_training.wait()
            print("Start model training")

        # Wait on master to become ready to access
        master_ready.wait()
        master_ready.clear()
        with master_bin_lock:
            print("Master bins unpacked:")
            mag_unpacked = [sample for sample in itertools.chain.from_iterable(magnitude_master_bin)]
            master_magnitude_unpacked.put(mag_unpacked)
            # master_phase_unpacked = [sample for sample in itertools.chain.from_iterable(phase_master_bin)]
        # Set master_ready so that dataprocessing can proceed
        master_ready.set()

        with start_fitting:
            start_fitting.notify_all()
        
        print("STATUS fit",magnitude_fitted.is_set(), phase_fitted.is_set() )
        # Wait twice, so wait on magnitude and phase fit to be finished
        magnitude_fitted.wait()
        phase_fitted.wait()
        
        # Both finished so reset flags
        magnitude_fitted.clear()
        phase_fitted.clear()

def magnitude_fit():
    """ Thread that is fitting magnitude data"""
    global current_magnitude_weights
    while not stop_threads.is_set():
        # Wait on model estimation to be ready
        with start_fitting:
            start_fitting.wait()
        current_magnitude_weights = fit_model(master_magnitude_unpacked)
        #TODO: Push new model parameters
        
        # Let model_estimion know that its done
        magnitude_fitted.set()
        print("Mag FITTED")

def phase_fit():
    """ Thread that is fitting phase data"""
    global current_phase_weights
    while not stop_threads.is_set():
        # Wait on model estimation to be ready
        with start_fitting:
            start_fitting.wait()
        current_phase_weights = fit_model(master_phase_unpacked)
        #TODO: Push new model parameters

        # Let model_estimion know that its done
        phase_fitted.set()
        print("phase FITTED")

# Serial com thread --> com with esp32
def serial_com():
    """ Takes the function argument message and transmits it to serial
    """    
    esp_serial = serial.Serial(esp_port, esp_baud_rate)

    esp_serial.close()
    esp_serial.open()
    while not stop_threads.is_set():

        # Skip if start up byte received
        if not mcu_ready.is_set():
            # Send start byte
            n_transmit_attempts = 10
            n_receive_attempts = 5
            start_byte = BitArray("0b01010101")
            
            for transmit_attempt in range(n_transmit_attempts):
                # n attempts to transmit
                esp_serial.write(start_byte)
                print("start byte attempt", transmit_attempt)

                for receive_attempt in range(n_receive_attempts):
                    # n attempts to receive
                    receive_byte = BitArray(esp_serial.read(1))
                    print("receive attempt", receive_attempt)
                    sleep(1)

                    # If received break
                    if receive_byte == BitArray("0b10101010"):
                        # Set mcu ready flag
                        mcu_ready.is_set()
                        break

                # Break out first loop            
                if mcu_ready.is_set():
                    print("Received start byte")
                    break   

            # If not received break out program
            if not mcu_ready.is_set():
                stop_threads.set()

        # Wait untill new instructions for FPGA
        transmit_instructions.wait()
        transmit_instructions.clear()

        # Collect packages and transmit package by package
        packages = [BitArray('0b0000'), BitArray('0b0001')]
        for package in packages:
            esp_serial.write(package)

def frequency_sweep(): 
    """ Thread that performs a frequency sweep """
    global min_frequency, max_frequency
    n_sweeps = 10
    # Generate frequencies at logscale
    frequencies = np.logspace(np.log10(min_frequency), np.log10(max_frequency), num=n_sweeps)

    while not stop_threads.is_set():
        # Wait till frequency_sweep is set:
        frequency_sweep.wait()
        
        for i, frequency in frequencies:
            # Transmit frequency stuff to FPGA

        frequency_sweep_finished.set()
            



# def main_thread():
#     """ Thread that is providing an interface between user and program
#         Deciding what frequency to drive
#     """
#     while not stop_threads.is_set():


# Main is only used to start threads
if __name__ == "__main__":

    # Events
    start_processing = threading.Event()

    # Global signals used for controlling threads
    data = queue.Queue()
    # master bin is ready to access
    master_ready.set()
    print("Check master", master_ready.is_set())
    # Initialize threads
    control_thread = threading.Thread(target=control_thread, args=())
    read_datastream = threading.Thread(target=read_datastream, args=())
    data_processing = threading.Thread(target=data_processing, args=())
    model_estimation = threading.Thread(target=model_estimation, args=())
    serial_com = threading.Thread(target=serial_com, args=())
    magnitude_fit = threading.Thread(target=magnitude_fit, args=())
    phase_fit = threading.Thread(target=phase_fit, args=())

    mock_thread = threading.Thread(target=mock_thread, args=())

    mock_thread.start()
    control_thread.start()
    read_datastream.start()
    data_processing.start()
    # model_estimation.start()
    # serial_com.start()
    # magnitude_fit.start()
    # phase_fit.start()

    # Stop at keyboard interrupt
    try:
        while True:
            sleep(1)
            if stop_threads.is_set():
                break
    except KeyboardInterrupt:
        stop_threads.set()
        with start_training:
            start_training.notify_all()
        data_processing.join()
        read_datastream.join()
        model_estimation.join()
        serial_com.join()
        magnitude_fit.join()
        phase_fit.join()
        print("END")
