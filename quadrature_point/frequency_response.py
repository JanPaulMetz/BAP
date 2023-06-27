""" Script for getting frequency response """
import time
import numpy as np
import serial
from bitstring import BitArray
from scipy import fft


class FrequencyResponse:

    # Constructor
    def __init__(self, comport, baudrate, n_sweeps):
        cmds = {"start sweep": 0b00000001,
                "data received": 0b00000010
               }
        def handshake():
            """ Performs handshake at startup, if it fails exit program"""
            # Remove boot data from byffer
            while ser.in_waiting:
                # nothing = ser.read()
                print(ser.read())

            transmit_attempts = 10
            receive_attempts = 5
            start_byte = bytes([255])

            received_flag = False
            not_received_flag = False

            # Initialize receive byte, prevent reference before assignment
            receive_byte = bytes([0])

            # Skip if start up byte received
            if not received_flag:
                # Send start byte
                
                for transmit_attempt in range(transmit_attempts):
                    # n attempts to transmit
                    ser.write(start_byte)
                    print("start byte attempt", transmit_attempt)

                    for receive_attempt in range(receive_attempts):
                        # n attempts to receive
                        if ser.in_waiting>0:
                            receive_byte = ser.read(1)
                        print("receive attempt", receive_attempt)
                        time.sleep(0.1)

                        # If received break
                        if receive_byte == bytes([125]):
                            # Set mcu ready flag
                            print("RECEIVED")
                            received_flag = True
                            break

                    # Break out first loop
                    if received_flag:
                        print("Received start byte")
                        break

                # If not received break out program
                if not received_flag:
                    not_received_flag = True
        
        def receive_data(serial,bytes_per_package,n_samples):
            """ Receive data from serial in packages
                1 package contains n_samples
                1 sample is represented by bytes_per_package

                Returns the all data points stored in a list
            """
            # Receive all samples in a package of samples
            package = serial.read(bytes_per_package*n_samples)

            # Convert package to an array of bits
            package_bits = BitArray(package)

            # Store 


        def receive_sweep(mcu_serial, cmds, n_sweeps):
            """ Receive sweep data and store """
            # First send desired number of sweeps
            mcu_serial.write(bytes([n_sweeps]))

            # Send desired sample size
            n_samples = mcu_serial.read(4)
            n_samples = int.from_bytes(n_samples, byteorder='little')
            print("SAMPLES", n_samples)

            # Collect data for n sweeps in matrix
            input_data = np.zeros((n_sweeps, n_samples))

            for i in range(n_sweeps):
                message = mcu_serial.read(2*n_samples)
                message_bits = 
                

        # Start serial com
        ser = serial.Serial(port=comport, baudrate=baudrate)
        ser.close()
        ser.open()

        # Handshake
        handshake()

        # Sweep
        receive_sweep(serial=ser, cmds=cmds, n_sweeps=n_sweeps)



    # Get magnitude response data
    
    
    # Get phase reponse data

    # Get cutoff frequency

if __name__=="__main__":
    frequency_response = FrequencyResponse(comport="COM7", baudrate=115200, n_sweeps=10)
    # 