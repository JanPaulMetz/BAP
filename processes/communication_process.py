""" Communcation process implementing protocol """
import time
import threading
import multiprocessing
import serial
from bitstring import BitArray
import struct
import numpy as np

from data_processing_functions import create_frequency_vector

class Communication:
    # 2 bytes
    input_buffer_size = 2*8
    n_transmit_attempts = 10
    n_receive_attempts = 5

    start_byte = bytes([255])
    

    def __init__(self,
                 baud_rate, comport,        # Serial
                 mcu_ready, mcu_not_ready,  # mcu status flags
                 update_fpga_rx) -> None:   # pipe, receiveing from system control
        
        self.baud_rate = baud_rate
        self.comport = comport
        self.mcu_ready = mcu_ready
        self.mcu_not_ready = mcu_not_ready
        self.update_fpga_rx = update_fpga_rx

    def serial_begin(self):
        """ Create serial object and start serial com"""
         # Construct serial object
        try:
            self.mcu_serial = serial.Serial(self.comport, self.baud_rate)
        except :
            print("NO PORT")
            self.mcu_not_ready.set()
        
        # close and open (start)
        self.mcu_serial.close()
        self.mcu_serial.open()

    def handshake(self):
        """ Performs handshake at startup, if it fails exit program"""
        # Initialize receive byte, prevent reference before assignment
        receive_byte = bytes([0])

        # Skip if start up byte received
        if not self.mcu_ready.is_set():
            # Send start byte
            
            for transmit_attempt in range(Communication.n_transmit_attempts):
                # n attempts to transmit
                self.mcu_serial.write(Communication.start_byte)
                print("start byte attempt", transmit_attempt)

                for receive_attempt in range(Communication.n_receive_attempts):
                    # n attempts to receive
                    if self.mcu_serial.in_waiting>0:
                        receive_byte = self.mcu_serial.read(1)
                    print("receive attempt", receive_attempt)
                    time.sleep(0.1)

                    # If received break
                    if receive_byte == bytes([125]):
                        # Set mcu ready flag
                        print("RECEIVED")
                        self.mcu_ready.set()
                        break

                # Break out first loop
                if self.mcu_ready.is_set():
                    print("Received start byte")
                    break

            # If not received break out program
            if not self.mcu_ready.is_set():
                self.mcu_not_ready.set()

    def led_cmd(self):
        """ when "01100001" =>  -- CMD: RX_LED                  [ascii: a] --> on/off """
        cmd = "a"
        self.mcu_serial.write(cmd.encode("utf-8"))

    def amplitude(self):
        """ when "01100010" =>  -- CMD: TX_AMPLITUDE            [ascii: b] -->"""
        cmd = "b"
        self.mcu_serial.write(cmd.encode("utf-8"))

    def frequencies(self, frequencies):
        """ when "01100011" =>  -- CMD: RX frequencies          [ascii: c] --> 4 bytes per frequency (tot 12 bytes)"""
        cmd = "c"
        self.mcu_serial.write(cmd.encode("utf-8"))

        for frequency in frequencies:
            # Send frequency as 4 bytes (float --> 4 bytes)
            frequency_bytes = struct.pack('f', frequency)
            self.mcu_serial.write(frequency_bytes)        

    def polynomial_features(self):
        """ when "01100100" =>  -- CMD: RX polynomial_features  [ascii: d]  --> """
        cmd = "d"
        self.mcu_serial.write(cmd.encode("utf-8"))

    def extra_feature(self):
        """ when "01100101" =>  -- CMD: RX extra_feature        [ascii: e] --> 2 bytes """
        cmd = "e"
        self.mcu_serial.write(cmd.encode("utf-8"))

    def magnitude_weights(self):
        """ when "01100110" =>  -- CMD: RX magnitude_weights    [ascii: f] --> 50 weights 2bytes per weight"""
        cmd = "f"
        self.mcu_serial.write(cmd.encode("utf-8"))

    def phasor_magnitude(self, frequencies, current_model_params, user_input_amplitudes):
        """ when "01101000" =>  -- CMD: RX phasor_magnitude     [ascii: h] --> 2 bytes per magnitude (tot 6) """
        cmd = "h"
        amplitudes = user_input_amplitudes
        # calculate phasor magnitude
        model_magnitude_list = []
        for frequency in frequencies:
            # Get frequency polynomials
            frequency_vector = create_frequency_vector(frequency)
            # get magnitude from model
            model_magnitude = np.dot(current_model_params, frequency_vector)

            model_magnitude_list.append(model_magnitude)
        
        system_input_magnitude = [amplitudes[i]/model_magnitude_list[i] for i in range(len(amplitudes))]

        # float --> 2 bytes
        short_data = [struct.pack('h', int(system_input_magnitude[i]*100)) for i in range(len(amplitudes))]

        # Encode
        self.mcu_serial.write(cmd.encode("utf-8"))

        for i in range(len(amplitudes)):
            self.mcu_serial.write(short_data[i])



    def model_id(self, id):
        """ when "01101010" =>  -- CMD: RX model_id             [ascii: j] --> 2 bytes """
        cmd = "j"
        id_bytes = struct.pack('h', int(id*100))
        self.mcu_serial.write(cmd.encode("utf-8"))
        self.mcu_serial.write(id_bytes)

    def update_model(self):
        """ when "01101011" =>  -- CMD: Update Model            [ascii: k] """
        cmd = "k"
        self.mcu_serial.write(cmd.encode("utf-8"))

def handshake_thread_target(mcu_serial, mcu_not_ready, mcu_ready):
    """ Performs handshake at startup, if it fails exit program"""
    global input_buffer_size
    # Skip if start up byte received
    if not mcu_ready.is_set():
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
    mcu_ready.wait()
    RX_LED = ord('a')
    RX_PHASOR_MAGNITUDE = ord('h')
    MODEL_ID = ord('j')
    UPDATE_MODEL = ord('k')

    while True:
        print("A",RX_LED )
        time.sleep(1)
        # RX_LED
        mcu_serial.write(RX_LED)
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
        mcu_serial.write(RX_LED)
        
        
    


def communication_process_target(port, baud_rate, mcu_not_ready, mcu_ready,
                                 update_fpga_rx):
# Create communication
    mcu_communication = Communication(baud_rate,port,mcu_ready,mcu_not_ready, update_fpga_rx)

# Begin communication
    mcu_communication.serial_begin()

# Handshake
    mcu_communication.handshake()

    # Create threads
    # # Startup handshake
    # handshake_thread = threading.Thread(
    #     target=handshake_thread_target        ,
    #     args=(mcu_serial,mcu_not_ready, mcu_ready)
    # )
    # Communication handler
    # communication_thread = threading.Thread(
    #     target=communication_thread_target,
    #     args=(mcu_serial,mcu_ready)
    # )

# Start threads
    # handshake_thread.start()
    # communication_thread.start()

    while True:

        # If there is content in the pipe
        if update_fpga_rx.poll():
            content_to_send = update_fpga_rx.recv()
            # GEt id
            model_id = content_to_send[0]
            # Get frequencies
            frequencies = content_to_send[1:7]
            # Get model params
            model_params = content_to_send[7:12]
            # Get amplitudes
            amplitudes = content_to_send[12:]

            # Send ID
            mcu_communication.model_id(model_id)
            # Send phasor magnitude
            mcu_communication.phasor_magnitude(frequencies,model_params,amplitudes)
            # Update
            mcu_communication.update_model()