import threading
import serial
from time import sleep
from bitstring import BitArray
import sys
from collections import deque
import numpy as np
import time
mcu_ready = False

mcu_serial = serial.Serial("COM10", 115200)
# input_buffer_size = 

# Skip if start up byte received
if not mcu_ready:
    # Send start byte
    n_transmit_attempts = 10
    n_receive_attempts = 5
    start_byte = bytes([255])
    receive_byte = 0
    for transmit_attempt in range(n_transmit_attempts):
        # n attempts to transmit
        mcu_serial.write(start_byte)
        print("start byte attempt", transmit_attempt)

        for receive_attempt in range(n_receive_attempts):
            # n attempts to receive
            if mcu_serial.in_waiting>0:
                receive_byte = mcu_serial.read(1)
            print("receive attempt", receive_attempt)
            time.sleep(0.1)

            # If received break
            if receive_byte == bytes([125]):
                # Set mcu ready flag
                print("RECEIVED")
                mcu_ready = True
                break

        # Break out first loop
        if mcu_ready:
            print("Received start byte")
            break

    # If not received break out program
    if not mcu_ready:
        mcu_not_ready = True

    """ Implementation of transmit pattern:
    Each command contains 1 command byte followed by content, stop message with update model CMD
    when "01100001" =>  -- CMD: RX_LED                  [ascii: a] --> on/off
    when "01100010" =>  -- CMD: TX_AMPLITUDE            [ascii: b] -->
    when "01100011" =>  -- CMD: RX frequencies          [ascii: c] --> 4 bytes per frequency (tot 12 bytes)
    when "01100100" =>  -- CMD: RX polynomial_features  [ascii: d]  --> 
    when "01100101" =>  -- CMD: RX extra_feature        [ascii: e] --> 2 bytes
    when "01100110" =>  -- CMD: RX magnitude_weights    [ascii: f] --> 50 weights 2bytes per weight
    when "01100111" =>  -- CMD: RX phase_weights        [ascii: g] NOT USED
    when "01101000" =>  -- CMD: RX phasor_magnitude     [ascii: h] --> 2 bytes per magnitude (tot 6)
    when "01101001" =>  -- CMD: RX phasor_phase         [ascii: i] NOT USED
    when "01101010" =>  -- CMD: RX model_id             [ascii: j] --> 2 bytes
    when "01101011" =>  -- CMD: Update Model            [ascii: k]
    
    """
    # RX_LED =  
from data_conversion import flatten, to_bytes, float_to_hex  
from math import ceil
RX_LED = ord('a')
RX_PHASOR_MAGNITUDE = ord('h')
MODEL_ID = ord('j')
UPDATE_MODEL = ord('k')
FP_SIZE = 16
FP_DATA_BYTES = ceil(FP_SIZE/8)
POLY_DIM = 10
EXTRA_DIM = 5
FREQ_DIM = 4

# Struct of commands
cmds = { "set_led": 0b01100001,
        "request_amplitude": 0b01100010,
        "param_frequencies": 0b01100011,
        "param_polynomial_features": 0b01100100,
        "param_extra_feature": 0b01100101,
        "param_magnitude_weights": 0b01100110,
        "param_phase_weights": 0b01100111,
        "param_phasor_magnitude": 0b01101000,
        "param_phasor_phase": 0b01101001,
        "param_model_id": 0b01101010
        }
polynomial_features = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]

raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(polynomial_features)]
byte_array = bytes([cmds['param_polynomial_features']] + flatten([to_bytes(i, 2) for i in raw_data]))

mcu_serial.write(byte_array)
while True:
    print("A",RX_LED )
    time.sleep(1)
    # RX_LED
    mcu_serial.write(bytes([97]))
    # TX_AMPLITUDE

    # RX frequencies

    # RX polynomial_features

    # RX extra_feature

    # RX magnitude_weights

    # RX phasor_magnitude
    mcu_serial.write(RX_PHASOR_MAGNITUDE)
    # RX model_id
    mcu_serial.write(MODEL_ID)
    # Update Model
    mcu_serial.write(UPDATE_MODEL)
    time.sleep(1)
    mcu_serial.write(bytes([97]))
        
        
    


sys.exit()
list_test = [1,2,3,4,4,3,3,2,2,2]
print(len(list_test[0:6]), list_test[0:6])
index = 0
if index:
    print("ey")

index.append(1)
if index:
    print("cool")
sys.exit()
 # Send start byte
mcu_serial = serial.Serial("COM12", 115200)
n_transmit_attempts = 10
n_receive_attempts = 5
start_byte = bytes([255])
mcu_ready = False
receive_byte = 0
for transmit_attempt in range(n_transmit_attempts):
    # n attempts to transmit
    mcu_serial.write(start_byte)
    print("start byte attempt", transmit_attempt)

    for receive_attempt in range(n_receive_attempts):
        # n attempts to receive
        if mcu_serial.in_waiting>0:
            print("HERA")
            receive_byte = mcu_serial.read(1)
        print("receive attempt", receive_attempt, receive_byte)
        time.sleep(1)

        # If received break
        if receive_byte == bytes([125]):
            # Set mcu ready flag
            print("RECEIVED")
            mcu_ready = True
            break

    # Break out first loop
    if mcu_ready:
        print("Received start byte")
        break

# If not received break out program
if not mcu_ready:
    print("FAILES")

n = 10
message_type_expected_time = [BitArray('0b00') for _ in range(10)]
sequence =[ 
    [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(8)],
    [BitArray('0b00') for _ in range(1)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(7)],
    [BitArray('0b00') for _ in range(2)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(6)],
    [BitArray('0b00') for _ in range(3)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(5)],
    [BitArray('0b00') for _ in range(4)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(4)],
    [BitArray('0b00') for _ in range(5)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(3)],
    [BitArray('0b00') for _ in range(6)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(2)],
    [BitArray('0b00') for _ in range(7)] + [BitArray('0b01'), BitArray('0b10')] + [BitArray('0b00') for _ in range(1)],
    [BitArray('0b00') for _ in range(8)] + [BitArray('0b01'), BitArray('0b10')],
    [BitArray('0b10')] +  [BitArray('0b00') for _ in range(9)],
    [BitArray('0b00') for _ in range(9)] + [BitArray('0b01')],
    [BitArray('0b00') for _ in range(10)]
]
for i in range(12):
    print(sequence[i])
    if sequence[i] ==message_type_expected_time:
        print(i)




ser = serial.Serial('COM11', 115200)
ser.close()
ser.open()
while True:
    data_bits = BitArray(ser.read(2*160))
    print(data_bits[0:640])
    print(data_bits[640:1280])
    print("helft")
    print(data_bits[1280:1920])
    print(data_bits[1920:])
    print("eind")
    # print()


def next_val(arg1=[0]):
    arg1[0] = arg1[0]+1
    return arg1[0]

for i in range(10):
    print(next_val())
    

# Data stream serial
stream_baud_rate= 115200
stream_port = 'COM11'

# Data stream
n_messages = int(800)
n_bytes = int(2*n_messages) # 2 bytes per message
n_bits = int(8*n_bytes)     # 8 bits per byte

# System constants
sample_rate = 65e6 # samples/sec
bin_size = int(n_messages - 2) # binsize of time data (in samples)
duration = bin_size/sample_rate

data_bin = bytearray()
data_lock = threading.Lock()
data_ready = threading.Condition(lock=data_lock)

stop_threads = threading.Event()

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
        data_to_store = stream_serial.read(800) # Data in bytes

        with data_lock:
            # store data to byte array
            data_bin.extend(data_to_store)
            data_ready.notify()  # Notify waiting threads
        # data_bin_2

def data_processing():
    while not stop_threads.is_set():

        with data_lock:
            # Send 800*2 bytes 
            # Wait until data_bin is ready
            
            data_ready.wait()
            data_to_process = data_bin[-2*n_bytes:].copy()

        if data_to_process.hex():
            # print(len(data_bin))
            print("SRTART")
            # with data_lock:
            #     data_bin.clear()

            data_bits = BitArray(data_to_process)
            # print(data_to_process)
            for i in range(2*n_bytes):
                message_type = data_bits[16*i: 16*i +2].copy()

                if message_type == BitArray('0b00'):
                    t = 1
                    # print("FOUND")
                elif message_type == BitArray('0b01'):
                    print("ID")
                

            
if __name__ == "__main__":

    read_datastream = threading.Thread(target=read_datastream, args=())
    data_processing = threading.Thread(target=data_processing, args=())

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