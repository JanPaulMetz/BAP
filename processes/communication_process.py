""" Communcation process implementing protocol """
import time
import threading
import multiprocessing
import serial
from bitstring import BitArray

input_buffer_size = 2*8 # 2 bytes

def handshake_thread_target(mcu_serial, mcu_not_ready, mcu_ready):
    """ Performs handshake at startup, if it fails exit program"""
    global input_buffer_size
    # Skip if start up byte received
    if not mcu_ready.is_set():
        # Send start byte
        n_transmit_attempts = 10
        n_receive_attempts = 5
        start_byte = BitArray("0b01010101")

        for transmit_attempt in range(n_transmit_attempts):
            # n attempts to transmit
            mcu_serial.write(start_byte)
            print("start byte attempt", transmit_attempt)

            for receive_attempt in range(n_receive_attempts):
                # n attempts to receive
                receive_byte = BitArray(mcu_serial.read(input_buffer_size))
                print("receive attempt", receive_attempt)
                time.sleep(1)

                # If received break
                if receive_byte == BitArray("0b10101010"):
                    # Set mcu ready flag
                    mcu_ready.set()
                    break

            # Break out first loop
            if mcu_ready.is_set():
                print("Received start byte")
                break

        # If not received break out program
        if not mcu_ready.is_set():
            mcu_not_ready.set()

def communication_thread_target(mcu_serial, mcu_ready):
    """ Thread activates if mcu is ready """
    mcu_ready.wait()
    while True:
        time.sleep(5)
    


def communication_process_target(port, baud_rate, mcu_not_ready, mcu_ready):

# Construct serial object
    try:
        mcu_serial = serial.Serial(port, baud_rate)
    except :
        print("NO PORT")
        mcu_not_ready.set()
        

    # close and open
    mcu_serial.close()
    mcu_serial.open()

# Create threads
    # Startup handshake
    handshake_thread = threading.Thread(
        target=handshake_thread_target,
        args=(mcu_serial,mcu_not_ready, mcu_ready)
    )
    # Communication handler
    communication_thread = threading.Thread(
        target=communication_thread_target,
        args=(mcu_serial,mcu_ready)
    )

# Start threads
    handshake_thread.start()
    communication_thread.start()

    while True:
        time.sleep(1)