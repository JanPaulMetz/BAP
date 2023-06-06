""" Implemention of the main process
    Functionality: provide user interface and control the system mode

    Implemented as a function that is composed of multiple threads 
    to prevent blocking by the user interface. This results in a responsive
    user interface
"""
# Import modules
import numpy as np
import time
import multiprocessing
import threading
import mmap

frequency_sweep_finished = threading.Event()

def frequency_sweep():
    """ Perform sweep """

    

def user_interface_thread_target(mcu_ready):
    """ Target of thread object, providing user interface"""
    mcu_ready.wait()
    
    # Wait on frequency, after freq sweep give user options
    while True:
        print("UI")
        time.sleep(1)

def control_thread_target(mcu_ready,model_params,model_params_lock,start_data_extraction):
    """ Target of thread object, controlling the system mode"""
    # If mcu is ready, start data extraction (thus whole system)
    mcu_ready.wait()
    start_data_extraction.set()

    # Trigger frequency sweep
    frequency_sweep.set()
    frequency_sweep_finished.wait()

    while True:
        
        time.sleep(1)


def main_process_target(model_params, model_params_lock, mcu_ready, start_data_extraction):
    """ Target of a process object, starting multiple threads"""
    # Wait for MCU to be ready

    # Create threads
    user_interface_thread = threading.Thread(target=user_interface_thread_target,
                                             args=(mcu_ready,))
    control_thread = threading.Thread(target=control_thread_target,
                                      args=(mcu_ready,model_params,model_params_lock,
                                            start_data_extraction)
    )

    # Start threads
    user_interface_thread.start()
    control_thread.start()

    while True:
        # Keep process running --> till terminated from main
        time.sleep(1)
