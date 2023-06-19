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
import random
import queue

frequency_sweep_finished = threading.Event()

# Initialize 
current_id_received_lock = threading.Lock()
current_id_received = 0

id_history_lock = threading.Lock()
id_history = []

new_model_params_lock = threading.Lock()
new_model_params = [0.01*random.randint(0,100) for _ in range(10)]

id_list_approved = []
id_list_approved_lock = multiprocessing.Lock()

id_list_not_empty = threading.Event()

def system_control_thread_target(mcu_ready, model_params, model_params_lock, start_data_extraction,
                                 frequency_sweep, bandwidth, update_fpga_tx, input_register,
                                 input_register_lock, new_user_input_rx,release_update_block):
    """ Controls system, freq sweep etc"""
    id_found = False

    def do_sweep():
        """ Doing frequency sweep"""

        # Create frequencies
        if bandwidth[0] == 0: # Log argument cant be 0
            frequencies = np.logspace(np.log10(0.1), np.log10(bandwidth[1]))
        else:
            frequencies = np.logspace(np.log10(bandwidth[0]), np.log10(bandwidth[1]))

        for frequency in frequencies:
            # Get new unique ID

            id_list_not_empty.wait() # Wait till id_list is filled
            with id_list_approved_lock:
                unique_id = [id_list_approved.pop(0)]

            # Send new ID, frequencies, model params, amplitude = 1
            list_to_send = [unique_id, temperature, frequency, 0, 0, 1, 0, 0] + new_model_params

            # Update communication process
            update_fpga_tx.send(list_to_send)
            
            # Update global input register
            with input_register_lock:
                input_register = np.append(input_register, list_to_send[0:7], axis=0)

            # Update global model parameters
            with model_params_lock:
                model_params = np.append(model_params, list_to_send[7:], axis=0)

            # Block untill ID is received back
            while not id_found:
                with id_history_lock:

                    # if sent id is received back
                    if unique_id in id_history:
                        # Find index
                        index = id_history.index(unique_id)

                        # Remove all older values (so from index 0)
                        for _ in range(index):
                            id_history.pop(0)

                        id_found = True

                # Give system-state time to lock
                time.sleep(0.2)

            # reset for next iteration
            id_found = False

        # Frequency sweep finished
        frequency_sweep.clear()

    # If mcu is ready, start data extraction (thus whole system)
    mcu_ready.wait()
    start_data_extraction.set()
    # if frequency_sweep.is_set():

    # Initially perfomr frequency sweep
    do_sweep()
    
    while True:
        
        if frequency_sweep.is_set():
            do_sweep()
        else:
            # Get new user input and send to fpga
            while new_user_input_rx.poll():
                # Only keep most new message (should be one)
                # |freq1,freq2,freq3|amp1,amp2,amp3|
                user_input = new_user_input_rx.recv()
            
            if not new_user_input_rx.poll():
                # If empty release update button block
                release_update_block.set()
            
            id_list_not_empty.wait() # Wait till id_list is filled
            with id_list_approved_lock:
                unique_id = [id_list_approved.pop(0)]

            with new_model_params_lock:
                # Send new ID, frequencies, model params, amplitude = 1
                list_to_send = [unique_id] + user_input + new_model_params

            # Update communication process
            update_fpga_tx.send(list_to_send)

            # Store sent list to input register
            with input_register_lock:
                input_register = np.append(input_register, list_to_send, axis=0)

        time.sleep(1)

def system_state_thread_target(current_id_rx, new_model_parameters_rx,
                               input_register, input_register_lock,
                               model_parameters, model_parameters_lock):
    """ keeps track of system state
        eg: what is current received ID
        What is newest model params
        Generate new ID for new model params"""
    global current_id_received
    global new_model_params
    global id_history
    while True:
        # Get current system state
        if current_id_rx.poll():
            with current_id_received_lock:
                current_id_received = current_id_rx.recv()
                current_id = current_id_received
            
            # Store to history
            with id_history_lock:
                id_history.append(current_id)
            
            # Throw out ID's older then current ID, in all memories
            with input_register_lock:
                # Check index of current ID, remove indices before this
                current_index_input_reg = np.where(input_register[:,0]==current_id)[0]
                print("CURRENT INDEX", int(current_index_input_reg))
                if int(current_index_input_reg) > 0:
                    input_register = input_register[int(current_index_input_reg):]

            with model_parameters_lock:
                print("Model params", model_parameters)

                # First assume more then 1 row long
                try:
                    current_index_model_params = np.where(model_parameters[:,0]==current_id)[0]
                
                # Else try for 1 row long (All except 1 row can be deleted)
                except:
                    current_index_model_params = np.where(model_parameters==current_id)[0]

                if int(current_index_model_params) > 0:
                    model_parameters = model_parameters[int(current_index_model_params),:]

        if new_model_parameters_rx.poll():
            new_model_params = new_model_parameters_rx.recv()

def id_generation_thread_target(input_register, input_register_lock):
    """ Generates new id and stores them 
        2^14 total possibilities
        Store 10
        Need to check if it is unique
    """
    global id_list_approved
    id_list = []
    list_size = 200
    while True:
        
        with id_list_approved_lock:
            id_list = id_list_approved.copy()
        # if list is not full
        if len(id_list)<list_size:
            # Generate ID 
            random_id = random.randint(0, 2**14)

            if random_id not in id_list:
                id_list.append(random_id)
        
        # if id_list is full
        if len(id_list)==list_size:
            # Check if a id is already in the register:
            indices_to_pop = []
            with input_register_lock:
                for i,id in enumerate(id_list):
                    index = np.where(input_register[:,0]==id)[0]
                    
                    # if index nonzero, track index
                    if index:
                        indices_to_pop.append(i)

            if indices_to_pop:
                id_list.pop(indices_to_pop)
            print("ID", id_list)
            with id_list_approved_lock:
                id_list_approved = id_list.copy()

                if id_list_approved:
                    id_list_not_empty.set()
                else:
                    id_list_not_empty.clear()

        time.sleep(0.5)


def system_control_process_target(model_params, model_params_lock, mcu_ready, start_data_extraction,frequency_sweep,
                                  current_id_rx, new_model_parameters_rx, bandwidth, input_register, input_register_lock,
                                  update_fpga_tx, new_user_input_rx,release_update_block):
    """ Target of a process object, starting multiple threads"""
# Create threads

    # Control
    system_control_thread = threading.Thread(target=system_control_thread_target,
                                      args=(mcu_ready,model_params,model_params_lock,
                                            start_data_extraction,frequency_sweep, bandwidth,
                                            update_fpga_tx, input_register, input_register_lock,
                                            new_user_input_rx,release_update_block)
    )
    # State
    system_state_thread = threading.Thread(target=system_state_thread_target,
                                           args=(current_id_rx, new_model_parameters_rx,
                                                 input_register, input_register_lock,
                                                 model_params, model_params_lock)
    )
    # ID generation
    id_generation_thread = threading.Thread(target=id_generation_thread_target,
                                            args=(input_register, input_register_lock)
    )
  
    # Start threads
    system_control_thread.start()
    system_state_thread.start()
    id_generation_thread.start()

    while True:
        # Keep process running --> till terminated from main
        time.sleep(1)
