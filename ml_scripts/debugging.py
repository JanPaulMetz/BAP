import threading
import serial
from time import sleep
from bitstring import BitArray
import sys
from collections import deque
import numpy as np
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
sys.exit()



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