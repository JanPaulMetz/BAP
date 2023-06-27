""" Communcation process implementing protocol """
from math import ceil
import time
import threading
import multiprocessing
import serial
from bitstring import BitArray
import struct
import numpy as np

# from data_processing_functions import create_frequency_vector
from data_conversion import flatten, to_bytes, float_to_hex
from data_processing_functions import *
import itertools

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
        "param_model_id": 0b01101010,
        "update_model" : 0b01101001
        }

# MOCK DATA: 

frequencies = [0x0180002A, 0x0300002A, 0x0100002A]         # 32 bit unsigned (Phase increase per clk cycle where 2^32 is 2*pi increase)
polynomial_features = [[4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
                       [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                       [6, 6, 6, 6, 6, 6, 6, 6, 6, 6]]     # FP_SIZE bit float
extra_feature = [1.0]                                               # FP_SIZE bit float
magnitude_weights = [0.003 for _ in range(0, POLY_DIM*EXTRA_DIM)]     # FP_SIZE bit float
phase_weights = [0.1 for _ in range(0, POLY_DIM*EXTRA_DIM)]         # FP_SIZE bit float
phasor_magnitude = [9000, 9000, 9000]                               # FP_SIZE bit float (Value between -2^15 to 2^15 -1)
phasor_phase = [1, 1, 1]                                   # FP_SIZE bit float (Value between 0 to 2*pi)
model_id = [1248]                                          # 14 bit unsigned (sent as 16 bits)


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
        # Toggle
        # cmd = 97/
        self.mcu_serial.write(bytes([cmds["set_led"], 6]))

    def amplitude(self): # Not used!
        """ when "01100010" =>  -- CMD: TX_AMPLITUDE            [ascii: b] -->"""
        cmd =  98#"b"
        self.mcu_serial.write(bytes([cmd])) #cmd.encode("utf-8")



    def frequencies(self, frequencies): # 4 Frequencies --> phase increase per sample (NOT NORMALIZED)
        """ when "01100011" =>  -- CMD: RX frequencies          [ascii: c] --> 4 bytes per frequency (tot 12 bytes)"""
        # cmd = 99 #"c"
        # self.mcu_serial.write(bytes([cmd]))
        
        phase_incr = []
        for frequency in frequencies:
            phase_incr.append(round((frequency*2**32)/(100e6)))

        # raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(phase_incr)]
        # byte_array = bytes([cmds['param_frequencies']] + flatten([to_bytes(i, 2) for i in raw_data]))
        # self.mcu_serial.write(byte_array)

        raw_data = flatten(phase_incr)
        byte_array = [cmds['param_frequencies']] + flatten([to_bytes(i, 4) for i in raw_data])
        self.mcu_serial.write(byte_array)
        # time.sleep(delay)
        

        
    def polynomial_features(self, polynomial_features, bandwidth): # [1, f , f^2 ....] NORMALIZED
        """ when "01100100" =>  -- CMD: RX polynomial_features  [ascii: d]  --> """
        raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(polynomial_features)]
        byte_array = [cmds['param_polynomial_features']] + flatten([to_bytes(i, FP_DATA_BYTES) for i in raw_data])
        self.mcu_serial.write(byte_array)
        # time.sleep(delay)
        # ser.write([cmd['set_led'], 3])

        # # TEST cmd = 100 #"d"
        # # Normalize frequencies and create vector [[1,f_norm, f_norm^2 ... f_norm^7], [...],[...],[..]]
        # frequencies_vector_normalized = []
        # for frequency in frequencies:
        #     # print("FREQ", frequency, type(frequency))
        #     frequencies_vector_normalized.append(create_feature_vector_normalized(frequency,bandwidth))
            

        # raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(frequencies_vector_normalized)]
        # byte_array = bytes([cmds['param_polynomial_features']] + flatten([to_bytes(i, 2) for i in raw_data]))
        
        # self.mcu_serial.write(byte_array)

    def extra_feature(self, extra_feature):
        """ when "01100101" =>  -- CMD: RX extra_feature        [ascii: e] --> 2 bytes """
        raw_data = [float_to_hex(a, FP_SIZE) for a in flatten([extra_feature])]
        byte_array = [cmds['param_extra_feature']] + flatten([to_bytes(i, FP_DATA_BYTES) for i in raw_data])
        self.mcu_serial.write(byte_array)

        # byte_array = bytes([cmds["param_extra_feature"] + flatten([to_bytes(power,2)])])
        # self.mcu_serial.write(byte_array)

    # TODO: cast to 2 bytes per weight
    def magnitude_weights(self, magnitude_weights):
        """ when "01100110" =>  -- CMD: RX magnitude_weights    [ascii: f] --> 50 weights 2bytes per weight"""
        raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(magnitude_weights)]
        byte_array = [cmds['param_magnitude_weights']] + flatten([to_bytes(i, FP_DATA_BYTES) for i in raw_data])
        self.mcu_serial.write(byte_array)
    
        # # self.mcu_serial.write(bytes([cmd]))
        # # weights = [to_bytes(weight, 2) for weight in weights]
        # print("WEIGHTS", weights)
        # raw_data = [float_to_hex(weight, FP_SIZE) for weight in flatten(weights)]
        # byte_array = bytes([cmds["param_magnitude_weights"]] + flatten([to_bytes(element, 2) for element in raw_data]))
        # self.mcu_serial.write(byte_array)

    def phasor_magnitude(self, amplitudes, frequencies, power, model_parameters, bandwidth):
        """ when "01101000" =>  -- CMD: RX phasor_magnitude     [ascii: h] --> 2 bytes per magnitude (tot 6) """
        # cmd = 104 #"h"
        # Calculate X_hat (magnitude that is on the ultrasound input)
        # Normalize frequencies and create vector [1,f_norm, f_norm^2 ... f_norm^7]
        frequencies_vector_normalized = []
        for frequency in frequencies:
            frequencies_vector_normalized.append(create_feature_vector_normalized(frequency,bandwidth))

        power_vector_normalized = create_feature_vector_normalized(power,bandwidth)

        X_hat_list = []
        for i, frequency_vector in enumerate(frequencies_vector_normalized):
            # multiply each element of power to the frequencies array
            # print("FREQ vector", frequency_vector)
            product_list = [[power_element*frequency_element for frequency_element in frequency_vector]for power_element in power_vector_normalized]
            flattened_product_list = list(itertools.chain(*product_list))

            # weights*product list (as dot operation) should result in scalar
            product_arr = np.array(flattened_product_list)
            # print("SIZES", product_arr.shape, np.shape(product_list), product_list)
            abs_H = np.dot(model_parameters, product_arr)

            X_hat_list.append(amplitudes[i]/abs_H)
        # self.mcu_serial.write(bytes(cmds["param_phasor_magnitude"]))

        # TODO: convert to 8 bytes (2bytes each) assumption float
        # time.sleep(delay)
        # ser.write([cmd['set_led'], 6])

        raw_data = [float_to_hex(X_hat, FP_SIZE) for X_hat in flatten(X_hat_list)]
        byte_array = bytes([cmds["param_phasor_magnitude"]] + flatten([to_bytes(i,FP_DATA_BYTES) for i in raw_data]))
        self.mcu_serial.write(byte_array) # Send list of magnitudes as packets of bytes (total 4*2 bytes)

    def model_id(self, model_id):
        """ when "01101010" =>  -- CMD: RX model_id             [ascii: j] --> 2 bytes """
        raw_data = flatten([model_id])
        byte_array = [cmds['param_model_id']] + flatten([to_bytes(i, 2) for i in raw_data])
        self.mcu_serial.write(byte_array)
        # time.sleep(delay)
        # self.mcu_serial.write([cmds['set_led'], 9])

        # self.mcu_serial.write(byte_array)

    def update_model(self):
        """ when "01101011" =>  -- CMD: Update Model            [ascii: k] """
        # cmd = 105 # "k"
        self.mcu_serial.write(bytes([cmds['update_model']]))

    # TODO: Communication with controller
    def calibrate_quadrature_point(self):
        """ Calibrate quadrature point """
        cmd = 103
        # Send q-point start command
        self.mcu_serial.write([cmd])

        # Wait for response
        # while
        # 

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
                                 update_fpga_rx, bandwidth):
# Create communication
    mcu_communication = Communication(baud_rate,port,mcu_ready,mcu_not_ready, update_fpga_rx)

# Begin communication
    mcu_communication.serial_begin()

# Handshake
    mcu_communication.handshake()

    while True:
        
        # If there is content in the pipe
        if update_fpga_rx.poll():
            content_to_send = update_fpga_rx.recv()
            print("UPDATE FPGA", len(content_to_send))
            # GEt id
            # TODO: Why 1:7
            model_id = content_to_send[0]
            print("model_id SHAPE", model_id)

            sec_feature = content_to_send[1]
            print("sec_feature SHAPE", sec_feature)
            # Get frequencies
            frequencies = content_to_send[2:6]
            print("frequencies SHAPE", frequencies)
            # Get amplitudes
            amplitudes = content_to_send[6:10]
            print("modamplitudesel_id SHAPE", amplitudes)
            # Get model params
            model_params = content_to_send[10:]
            print("model_params SHAPE", len(model_params))
            

            # Test poly features
            # polynomial_features = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            #            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            #            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]
            frequencies = [3,4,2,1]
            # Send ID
            mcu_communication.led_cmd()
            mcu_communication.polynomial_features(frequencies, bandwidth)
            mcu_communication.model_id(model_id)
            mcu_communication.frequencies(frequencies)
            mcu_communication.magnitude_weights(model_params)
            mcu_communication.phasor_magnitude(amplitudes, frequencies, sec_feature, model_params, bandwidth)
            mcu_communication.extra_feature(1)
            #amplitudes, frequencies, power, model_parameters, bandwidth


            # # Send phasor magnitude
            # mcu_communication.phasor_magnitude(frequencies,model_params,amplitudes)
            # Send frequencies 
            
            # # Update
            mcu_communication.update_model()