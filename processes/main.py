""" Main--> Setup all processes"""

# Import modules
import numpy as np
import multiprocessing
import queue
import mmap

# Import processes
from read_datastream_process import *
from data_processesing_process import *
from main_process import *
from communication_process import *
from data_training_process import *

## System configurations:

# Data stream config
data_stream_port = 'COM11'
data_stream_baud_rate = 115200

n_packages = int(80)        # 1 package = 2 bytes
n_bytes = int(2*n_packages)
n_bits = int(8*n_bytes)

# MCU serial config

# System constants
sample_rate = 65e6              # [samples/sec]
bin_size = int(n_packages-2)    # binsize of timedata [samples]
bandwith = [1.58e6, 1.68e6]     # bandwith of system  [Hz]


def main():
    """ Main function: initializes required globals, flags etc. Then creates multiple processes"""
# mmaps (global memory)

    # Model parameters |ID|magnitude weights| = |1|10| (size)
    model_params_filename = "model_parameters.bin"
    model_params_lock = multiprocessing.Lock()
    model_params_numcols = 11
    default_params = np.random.rand(1,model_params_numcols)
    # Make test params
    default_params[0,0] = 2
    tes_params1 = default_params.copy()
    
    default_params[0,0] = 0.4722900390625
    tes_params2 = default_params.copy()

    default_params[0,0] = 5
    tes_params3 = default_params.copy()
    with open(model_params_filename, mode="w+b") as file:
        # Get file size and truncate file to that size
        file_size = np.dtype(np.float64).itemsize*model_params_numcols
        file.truncate(file_size)

        # get memory-mapped file
        model_params_mmaped_file = mmap.mmap(file.fileno(), 0)

        # Create the shared array that will represent the file
        model_params_shared_array = np.ndarray(shape=(0, model_params_numcols),
                                                dtype=np.float64, buffer=model_params_mmaped_file)
        
        # Append default parameters
        model_params_shared_array = np.append(model_params_shared_array, default_params, axis=0)
        
        # Add test params
        model_params_shared_array = np.append(model_params_shared_array,tes_params1,  axis=0)
        model_params_shared_array = np.append(model_params_shared_array,tes_params2,  axis=0)
        model_params_shared_array = np.append(model_params_shared_array,tes_params3,  axis=0)
        print("shared array content", model_params_shared_array)
        # Close file
        model_params_mmaped_file.close()
    
    # Input register |ID|freq1|freq2|freq3|amplitude1|amplitude2|amplitude3| --> size = 7
    input_register_filename = "input_register.bin"
    input_register_lock = multiprocessing.Lock()
    input_register_numcols = 7

    default_input = np.random.rand(1,input_register_numcols)
    default_input[0,0] = 0.4722900390625

    with open(input_register_filename, mode="w+b") as file:
        # Get filesize (columns)
        file_size = np.dtype(np.float64).itemsize*input_register_numcols
        file.truncate(file_size)

        # Get memory mapped file
        input_register_mmaped_file = mmap.mmap(file.fileno(), 0)

        # Create shared array that will be used to access this mmaped file
        input_register_shared_array = np.ndarray(shape=(0, input_register_numcols),
                                                 dtype=np.float64, buffer=input_register_mmaped_file)
        
        # Append default input
        input_register_shared_array = np.append(input_register_shared_array, default_input, axis=0)
        
        # Close mmaped file
        input_register_mmaped_file.close()

    # Second feature
    # Time samples  
    
# Locks (global locks)
    
# Queue's (shared memory of multiple processes)

# Pipe's (shared memory of process couples)

    # read_data_stream_process --> data_processing_process 
    data_to_process_tx, data_to_process_rx = multiprocessing.Pipe()

    # magnitude samples (process_data) --> tran_data 
    magnitude_samples_tx, magnitude_samples_rx = multiprocessing.Pipe()

# Flags (signals)
    # data_processing_process --> read_data_stream_process
    # default: set
    start_data_extraction = multiprocessing.Event()
    start_data_extraction.set()

# Create processes
    # main process
    main_process = multiprocessing.Process(
        target=main_process_target, args=(model_params_shared_array, model_params_lock)
    )
    # datastream reading
    read_datastream_process = multiprocessing.Process(
        target=read_datastream_process_target,
        args=(data_stream_port, data_stream_baud_rate, n_packages, data_to_process_tx,
              start_data_extraction)
    )
    # data processing
    data_processing_process = multiprocessing.Process(
        target=data_processing_process_target,
        args=(data_to_process_rx,start_data_extraction,
              model_params_shared_array, model_params_lock,         # model_params shared memory
              input_register_shared_array, input_register_lock,     # input_register shared memory
              bin_size, sample_rate, magnitude_samples_tx)
    )
    # main
    # communication
    # data training
    data_training_process = multiprocessing.Process(
        target=data_training_process_target,
        args=(magnitude_samples_rx,)
    )


# Start processes
    main_process.start()
    read_datastream_process.start()
    data_processing_process.start()
    data_training_process.start()
    

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # terminate process at keyboard interrupt
        main_process.terminate()
        read_datastream_process.terminate()
        data_processing_process.terminate()
        data_training_process.terminate()


if __name__=="__main__":
    main()
    