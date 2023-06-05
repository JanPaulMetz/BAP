""" Implementation of data training process """

import multiprocessing
import threading
import time

def sample_manager_thread_target(magnitude_samples_rx):
    """ Updates bin containing all magnitude samples """
    while True:
        print("..")
        time.sleep(2)

def train_magnitude_thread_target():
    """ Train the data bin"""
    while True:
        print("...")
        time.sleep(2)

def store_parameters_thread_target():
    """ Store the obtained model parameters to global mem """
    while True:
        print( '..')
        time.sleep(2)

def data_training_process_target(magnitude_samples_rx):
    """ Target for process data training"""
# Create Threads
    # Sample manager
    sample_manager_thread = threading.Thread(
        target=sample_manager_thread_target,
        args=(magnitude_samples_rx,)
    )
    # Train Magnitude
    train_magnitude_thread = threading.Thread(
        target=train_magnitude_thread_target,
        args=()
    )
    # Store Parameters
    store_parameters_thread = threading.Thread(
        target=store_parameters_thread_target,
        args=()
    )

# Start Threads
    sample_manager_thread.start()
    train_magnitude_thread.start()
    store_parameters_thread.start()

    while True:
        time.sleep(1)
