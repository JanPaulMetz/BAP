
import time
import multiprocessing
import threading

def datastream_thread_target():
    """ Mocks the data_stream"""
    print("nothing")

def receive_mcu_thread_target():
    """ Mocks the mcu incoming serial"""
    print("nothing")

def simulation_process_target(d):
    """ Process for simulation
        Input from MCU and output to datastream
    """

    datastream_thread = threading.Thread(target=datastream_thread_target,
                                         args=()
    )
    receive_mcu_thread = threading.Thread(target=receive_mcu_thread_target,
                                          args=())
    datastream_thread.start()
    receive_mcu_thread.start()
 
    while True:
        time.sleep(1)
