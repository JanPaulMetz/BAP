""" Main--> Setup all processes"""

# Import modules
import numpy as np
import multiprocessing
import queue
import mmap
import sys

# GUI imports
from GUI_class import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

# Import processes
from read_datastream_process import *
from data_processesing_process import *
from system_control_process import *
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
mcu_port = 'COM10'
mcu_baud_rate = 115200

# System constants
sample_rate = 65e6              # [samples/sec]
bin_size = int(n_packages-2)    # binsize of timedata [samples]
bandwidth = [0,1]# [1.58e6, 1.68e6]     # bandwith of system  [Hz]


def main():
    """ Main function: initializes required globals, flags etc. Then creates multiple processes"""
# mmaps (global memory)

    # Model parameters history |ID|magnitude weights| = |1|10| (size)
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
    
    # Second feature register|ID|secondfeature|
    second_feature_register_filename = "second_feature.bin"
    second_feature_register_lock = multiprocessing.Lock()
    second_feature_numcols = 2

    default_second_feature = np.array([0.4722900390625,20])

    with open(second_feature_register_filename, mode="w+b") as file:
        # Get filesize (columns)
        file_size = np.dtype(np.float64).itemsize*second_feature_numcols
        file.truncate(file_size)

        # Get memory mapped file
        second_feature_mmaped_file = mmap.mmap(file.fileno(), 0)

        # Create shared array that will be used to access this mmaped file
        second_feature_shared_array = np.ndarray(shape=(0, input_register_numcols),
                                                 dtype=np.float64, buffer=second_feature_mmaped_file)
        
        # Append default input
        second_feature_shared_array = np.append(second_feature_shared_array, default_input, axis=0)
        
        # Close mmaped file
        second_feature_mmaped_file.close()

# Locks (global locks)
    
# Queue's (shared memory of multiple processes)

# Pipe's (shared memory of process couples)

    # read_data_stream_process --> data_processing_process
    data_to_process_tx, data_to_process_rx = multiprocessing.Pipe()

    # magnitude samples (process_data) --> train_data 
    magnitude_samples_tx, magnitude_samples_rx = multiprocessing.Pipe()

    # Updated model parameters train_data-->control process
    new_model_parameters_tx, new_model_parameters_rx = multiprocessing.Pipe()

    # Current id data processing --> control process
    current_id_tx, current_id_rx = multiprocessing.Pipe()

    # update_fgpa: control --> communication:
    #|ID|f1,f2,f3|amp1,amp2,amp3|model_params|
    update_fpga_tx, update_fpga_rx = multiprocessing.Pipe()

    # new user input pipe
    new_user_input_tx, new_user_input_rx = multiprocessing.Pipe()

    # Data to plot
    frequency_plot_tx, frequency_plot_rx = multiprocessing.Pipe()
    temperature_plot_tx, temperature_plot_rx = multiprocessing.Pipe()
    magnitude_plot_tx, magnitude_plot_rx = multiprocessing.Pipe()

# Flags (signals)
    # data_processing_process --> read_data_stream_process
    # default: set
    start_data_extraction = multiprocessing.Event()

    mcu_not_ready = multiprocessing.Event()
    mcu_ready = multiprocessing.Event()

    # Activates frequency sweep
    # By default set so that after start it begins with sweep
    frequency_sweep = multiprocessing.Event()
    frequency_sweep.set()

    # data processing -> system control (notify new id in pipe)

    # Magnitude data updated
    magnitude_data_updated = multiprocessing.Event()

    # Release udpate button
    release_update_block = multiprocessing.Event()

# Create processes
    # system control process
    system_control_process = multiprocessing.Process(
        target=system_control_process_target,
        args=(model_params_shared_array, model_params_lock,
              mcu_ready, start_data_extraction, frequency_sweep,
              current_id_rx,new_model_parameters_rx, bandwidth,
              input_register_shared_array, input_register_lock,
              update_fpga_tx, new_user_input_rx,release_update_block)
    )
    # w reading
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
              bin_size, sample_rate, magnitude_samples_tx,
              current_id_tx, second_feature_shared_array,
              second_feature_register_lock)
    )

    # communication
    communication_process = multiprocessing.Process(
        target=communication_process_target,
        args=(mcu_port, mcu_baud_rate, mcu_not_ready, mcu_ready,
              update_fpga_rx)
    )
    # data training
    data_training_process = multiprocessing.Process(
        target=data_training_process_target,
        args=(magnitude_samples_rx,bandwidth,new_model_parameters_tx,
              frequency_plot_tx, temperature_plot_tx,magnitude_plot_tx, magnitude_data_updated)
    )


# Start processes
    system_control_process.start()
    read_datastream_process.start()
    data_processing_process.start()
    communication_process.start()
    data_training_process.start()

# MAIN --> CONTROL AND GUI

# GUI Callbacks
    def frequency_sweep_callback():
        """ Initiates freq sweep, callback of GUI"""
        # Trigger frequency sweep
        print("SWEEEEP")
        frequency_sweep.set()
    
    def user_input_callback(frequencies, amplitudes):
        """ If user hits update button """
        # Send user input to system control
        data_to_send = [frequencies] + [amplitudes]
        new_user_input_tx.send(data_to_send)
    
    def update_plot(window,frequency_plot_rx, temperature_plot_rx, magnitude_plot_rx,
                                  magnitude_data_updated):
        while True:
            if magnitude_data_updated.is_set():
                frequency_to_plot = frequency_plot_rx.recv()
                temperature_to_plot = temperature_plot_rx.recv()
                magnitude_to_plot = magnitude_plot_rx.recv()
                window.update_plot(frequency_to_plot, magnitude_to_plot)

# Start GUI
    
    # GUI application
    app = QApplication(sys.argv)

    # GUI window
    window = MainWindow(user_input_callback, frequency_sweep_callback)
                        # frequency_plot_rx, temperature_plot_rx, magnitude_plot_rx,
                        # magnitude_data_updated)

    # Show the main window
    window.show()

    # Plot thread
    plot = threading.Thread(target=update_plot,
                            args=(window,frequency_plot_rx, temperature_plot_rx, magnitude_plot_rx,
                                  magnitude_data_updated))
    plot.start()
    # Start the application event loop
    app.exec_()
    # sys.exit()

    try:
        while True:
            time.sleep(0.01)
            # # Update plot when magnitude data is updated
            # frequency_to_plot = [1,1000,100000]
            # temperature_to_plot = temperature_plot_rx.recv()
            # magnitude_to_plot =[2,3,3]
            # print("HERA")
            # window.update_plot(frequency_to_plot, magnitude_to_plot)
            # if magnitude_data_updated.is_set():
            #     print("HERB")
            #     magnitude_data_updated.clear()

            #     frequency_to_plot = frequency_plot_rx.recv()
            #     temperature_to_plot = temperature_plot_rx.recv()
            #     magnitude_to_plot = magnitude_plot_rx.recv()

                

            if mcu_not_ready.is_set():
                print("NO PORT or FAILED MCU HANDSHAKE")
                # terminate process at keyboard interrupt
                system_control_process.terminate()
                read_datastream_process.terminate()
                data_processing_process.terminate()
                communication_process.terminate()
                data_training_process.terminate()
                break
    except KeyboardInterrupt:
        # terminate process at keyboard interrupt
        system_control_process.terminate()
        read_datastream_process.terminate()
        data_processing_process.terminate()
        communication_process.terminate()
        data_training_process.terminate()


if __name__=="__main__":
    main()
    