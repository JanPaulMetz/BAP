""" Toplevel script containing threads"""
from time import sleep
import random
import threading
import queue
import serial

from scipy.fft import fft, fftfreq
from scipy import signal
import numpy as np
import pandas as pd

import sys
from bitstring import BitArray

from data_processing import message_to_float, calculate_magnitude_response,get_fft_index

# Data stream serial
stream_baud_rate= 115200
stream_port = 'COM11'

# Data stream
n_messages = int(80)
n_bytes = int(2*n_messages) # 2 bytes per message
n_bits = int(8*n_bytes)     # 8 bits per byte

# Data Processing
ready_to_process = True # used to check whether processing thread is ready
current_ID = 0
current_temperature = 0

# System constants
sample_rate = 65e6
bin_size = int(n_messages - 2) # binsize of time data

# Window
hann_window = np.copy(signal.windows.hann(int(bin_size), False))

# Contains data from stream input
data_bin = bytearray()
data_lock = threading.Lock()

# DataFrame containing ID's and frequency components with amplitude that are used for input
n_frequencies = 3
input_df = pd.DataFrame({'ID': [1.11328125], 'Frequency1':[1.6e6], 'Amplitude1':[1],'Frequency2':[1.601e6],
                          'Amplitude2':[0.3],'Frequency3':[1.61e6], 'Amplitude3':[0.57]})

# Keyboard Interrupt signal
stop_threads = threading.Event()

# Main thread
def main_thread():
    """ The main thread is responsible for continuously reading
        data from the incoming datastream (Fast!). 
        It also acts as a main function that is controlling
        other threads. Most important is that data is read 
        continuously and calculations are performed elsewhere.
    """
    sleep(5)
    print("main thread")

def read_datastream():
    """ Function to read from serial datastream, store it to global bin
    """
    # Initialize serial port
    stream_serial = serial.Serial(stream_port, stream_baud_rate)

    # Make sure it is not already opened (reopen)
    stream_serial.close()
    stream_serial.open()

    # Always except when keyboard interrupt
    while not stop_threads.is_set():
        data_to_store = stream_serial.read(n_bytes) # Data in bytes

        with data_lock:
            # store data to byte array
            data_bin.extend(data_to_store)

# Data processing thread
def data_processing(start):
    """ The intention is to use this function as a threaded function
        It calculates the magnitude and phase response of the current
        time data (for a max of 4 frequency components at a time)
        the start_processing condition is used as trigger for starting
        the processing of the time-domain data
    """

    while not stop_threads.is_set():
        
        with data_lock:
            # Get data from data_bin (twice the size for locking on the ID byte)
            data_to_process = data_bin[0:2*n_bytes]
            
            # Clear data_bin, so that it does not overflow
            data_bin.clear()

        data_to_process_string = data_to_process.hex()

        # Only process non empty bins
        if data_to_process_string:
            # Get opcode from first byte 00 = time data, 10 = ID, 01 = second feature
            print("data", len(data_to_process))
            # Convert bytearray to bitarray
            data_to_process_bits = BitArray(data_to_process)
            print(data_to_process_bits)
            message_length = 2*8 # 2 bytes in bits
            # print('length', len(data_to_process_bits))

            # Message types:
            type_time_data = BitArray('0b00')
            type_second_feature = BitArray('0b10')
            type_ID = BitArray('0b01')
            type_error = BitArray('0b11')

            # Extract databin of length n_messages (1 message is 2 bytes) starting with ID byte
            # print("n_bits",n_bits)
            for i in range(2*n_messages):

                # Check for every 2 bytes the message type
                message_type = data_to_process_bits[message_length*i: message_length*i + 2]
                
                # if message is of type ID, get 1 binlength from total data, starting with ID byte
                if message_type == type_ID:
                    data_to_process_bits = data_to_process_bits[message_length*i: message_length*i + n_bits]
                    break
            
            # print('length', len(data_to_process_bits))
            # print("message",data_to_process_bits)
            
            time_domain_samples_out = []
            # For each 2 bytes (message) extract the data and convert to float
            for i in range(n_messages):

                # Two MSB's --> message type
                message_type = data_to_process_bits[message_length*i: message_length*i + 2]
                # print("Message type", message_type)

                # 14 LSB's --> message content
                message_content = data_to_process_bits[message_length*i+2: message_length*i + 16]
            
                # Time message
                if message_type == type_time_data:
                    message_float = message_to_float(message_content)
                    print(message_content)
                    print(message_float)
                    # Append all time domain samples to this list
                    time_domain_samples_out.append(message_float)

                # ID
                elif message_type == type_ID:
                    message_float = message_to_float(message_content)
                    current_ID = message_float
                    print("ID", message_float)
                    
                # Temperature
                elif message_type == type_second_feature:
                    message_float = message_to_float(BitArray('0b01101010101010'))
                    current_temperature = message_float
                    # print("Temperature")
                # Error in message
                elif message_type == type_error:
                    print("Error in message")
            
            # Data is extracted, start getting frequency response of this data bin

            # Window time signal
            windowed_output = hann_window*time_domain_samples_out

            # Get normalized singlesided output fft
            output_fft = fft(windowed_output)
            output_fft_normalized = output_fft/len(output_fft)
            output_fft_normalized_r = output_fft_normalized[0:len(output_fft_normalized)//2]

            # Extract data from input_df
            current_index = input_df.loc[input_df['ID']==current_ID].index[0]
            current_input = input_df.loc[current_index]
            frequencies = current_input[["Frequency1","Frequency2","Frequency3"]]
            amplitudes = current_input[["Amplitude1","Amplitude2","Amplitude3"]]
            for i in range(n_frequencies):
                frequency = frequencies[i]
                amplitude = amplitudes[i]

                # skip if frequency has amplitude 0
                if amplitude > 0:
                    fft_index = get_fft_index(frequency, sample_rate, bin_size)
                    magnitude_response = calculate_magnitude_response(output_fft_normalized_r, amplitude, fft_index)
                    print("magnitude respo",magnitude_response)

                print("index", amplitude)
                print("content", frequency)
                # if n_frequencies > 0:


            print(time_domain_samples_out)
            print(len(time_domain_samples_out))
            # calculate_frequency_response(current_ID, current_temperature,time_domain_samples_out ,time_domain_samples_out, sample_rate, bin_size)
                
# Process time-domain data
def process_time_data():
    """ Thread that is processing the time-domain data.
        Starts processing if start_processing is set
        Immediatly after this is started, it wil reset ready_to_process.
        After it is finished, it will set ready_to_process.
    """
    while not stop_threads.is_set():
        # Wait on trigger to start
        start_processing.wait()
        # Reset ready_to_process
        ready_to_process = False

        # Set ready_to_process
        ready_to_process = True

        # Trigger start_processing
        start_processing.set()

# Update input DataFrame
def updata_input_data_frame():
    """ When data corresponding to an ID is requested
        pop de 
    
    """


# Model estimation thread
def model_estimation():
    """ Fits a polynomial to the data that is containing the phase and 
        magnitude response.
    """
    sleep(3)
    print("mdoel thread")

# Serial com thread --> com with esp32
def serial_com():
    """ Takes the function argument message and transmits it to serial
    """
    sleep(5)
    print("serial thread")


# Main is only used to start threads
if __name__ == "__main__":

    # Events
    start_processing = threading.Event()

    # Global signals used for controlling threads
    data = queue.Queue()
    # Initialize threads
    read_datastream = threading.Thread(target=read_datastream, args=())
    data_processing = threading.Thread(target=data_processing, args=(start_processing, ))
    model_estimation = threading.Thread(target=model_estimation, args=())
    serial_com = threading.Thread(target=serial_com, args=())

    read_datastream.start()
    data_processing.start()


    # Stop at keyboard interrupt
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        stop_threads.set()
        data_processing.join()
        read_datastream.join()
        print("END")
