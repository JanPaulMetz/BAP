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

def user_interface_thread_target():
    """ Target of thread object, providing user interface"""
    while True:
        print("UI")
        time.sleep(1)

def system_mode_thread_target(shared_array,lock):
    """ Target of thread object, controlling the system mode"""
    while True:
        # Try reading:
        with lock:
            print(shared_array[0])
        time.sleep(1)
        default_params = np.random.rand(1,11)
        # with lock:
        #     shared_array = np.append(shared_array,default_params, axis=0)
        #     print("NEW", shared_array)
        # time.sleep(1)
        # with lock:
        #     shared_array = np.delete(shared_array, 0, axis=0)


def main_process_target(shared_array, lock):
    """ Target of a process object, starting multiple threads"""
    # Wait for MCU to be ready

    # Create threads
    user_interface_thread = threading.Thread(target=user_interface_thread_target,
                                             args=())
    system_mode_thread = threading.Thread(target=system_mode_thread_target,
                                          args=(shared_array,lock)
    )

    # Start threads
    user_interface_thread.start()
    system_mode_thread.start()

    while True:
        # Keep process running --> till terminated from main
        time.sleep(1)
