""" Implementation of the datastream handler. It reads from datastream
    and processes packages with 2*package_size"""

# Import modules
import multiprocessing
import threading
import queue
import time
import serial
from collections import deque

from read_datastream_functions import *

def read_datastream_thread_target(port, baud_rate, n_packages, data_bin, data_lock,new_data):
    """ Thread reading datastream
        
    inputs: port        --> Serial port
            baud_rate   --> serial baud-rate
            package_size--> size of received package (1 package is 2 bytes)
            data_lock   --> locks data bin
    """
    # Initialize serial object
    stream_serial = serial.Serial(port, baud_rate)

    # Make sure it is not already open
    stream_serial.close()
    stream_serial.open()

    # Always fill buffer
    n_bytes = 2*n_packages
    buffer_size = 2*n_bytes*2       
    print("opened")
    while True:
        data_to_store = stream_serial.read(buffer_size)

        with data_lock:
            print("data read")
            # deque is deleting oldest data
            data_bin.appendleft(data_to_store)
            new_data.set()

        # data_bits = BitArray(data_to_store)
        # print("in read enz")
        # print(data_bits[0:640])
        # print(data_bits[640:1280])
        # print(data_bits[1280:1920])
        # print(data_bits[1920:])
        # print("eind read")


def extract_packages_thread_target(n_packages,data_to_process_tx, start_data_extraction, data_bin, data_lock,new_data):
    """ Thread extracting packages from data"""
    n_bytes = int(2*n_packages)
    data_to_process = bytearray()
    while True:
        # Wait on data_processing_process to be ready for receiving data
        start_data_extraction.wait()
        # Wait on new data, if no new data, data extraction is not required
        new_data.wait()
        print("DATA EXTRACTION")
        with data_lock:
            # Get
            data_to_process = data_bin.pop()

            # Clear
            new_data.clear()
            # data_bin.clear()

        # Extract databin startin with ID byte
   
        data_to_process_bits = BitArray(data_to_process)
        sync_status, data_synced = sync_on_id(data_to_process_bits, n_bytes)
        print("data_synced size", len(data_synced))
        # Data is synced --> Convert to float
        if sync_status:
            # If sync succesfull
            # print(data_synced)

            # Convert sorted list to decimal
            package_size = 2*8 # 2 bytes = 16 bits
            data_synced_decimal = []
            for i in range(n_packages):
                # Get only 14 content bits

                package_content = data_synced[package_size*i + 2: package_size*i + package_size]
                # Append decimal content
                # print("SIZE of content", len(package_content))
                data_synced_decimal.append(single_point_to_decimal(package_content))

            # Data is now in decimal [ID,Temp,T,T,T,T ......, T]
            # print("DECIMAL", data_synced_decimal, len(data_synced_decimal))

            # Send data --> Dataprocessing
            data_to_process_tx.send(data_synced_decimal)
   

def read_datastream_process_target(port, baud_rate, n_packages, data_to_process_tx, start_data_extraction):
    """ Target of data_stream process
        Continuously read from data_stream
        and extract packages
    """
# Queue
    # Data bin 
    data_bin = deque(maxlen=2*n_packages)
    data_lock = multiprocessing.Lock()
# Flags 
    new_data = threading.Event() # Only if new data, extract data (end lock data_lock)

# Create Threads
    read_datastream_thread = threading.Thread(target=read_datastream_thread_target,
                                       args=(port,baud_rate, n_packages, data_bin, data_lock, new_data))
    extract_packages_thread = threading.Thread(target=extract_packages_thread_target,
                                        args=(n_packages,data_to_process_tx, start_data_extraction, data_bin, data_lock, new_data))
    # Start threads
    read_datastream_thread.start()
    extract_packages_thread.start()

    # Keep process alive --> Terminated in main.py
    while True:
        time.sleep(1)
