import time
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy import fft
import serial
from bitstring import BitArray
import struct
# from startup_pc_mcu import start_pc_mcu


COMPORT = "COM5"
BAUD_RATE = 115200

# calibration samples
N_SAMPLES = 180
SAMPLE_PERIOD = 0.02 #??
SAMPLE_RATE = 1/SAMPLE_PERIOD # Samples/seconds (1/sample_period)

def handshake():
    """ Performs handshake at startup, if it fails exit program"""
    transmit_attempts = 10
    receive_attempts = 10
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
            # ser.write(bytes(255))
            print("start byte attempt", transmit_attempt)

            for receive_attempt in range(receive_attempts):
                # n attempts to receive
                if ser.in_waiting>0:
                    receive_byte = ser.read(1)
                print("receive attempt", receive_attempt)
                time.sleep(0.1)

                # If received break
                print("SERIAL", ord(receive_byte), bytes([125]))
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

def sine_func(x, amplitude, frequency, phase, offset, offset_slope):
    return amplitude* np.sin(2 * np.pi * frequency * x + phase) + offset + offset_slope*x

def first_derivative(x, amplitude, frequency, phase, offset_slope):
    return (2 * np.pi * frequency)*amplitude*np.cos(2* np.pi * frequency * x + phase) + offset_slope

def second_derivative(x, amplitude, frequency, phase):
    return -((2 * np.pi * frequency)**2)*amplitude*np.sin(2* np.pi * frequency * x + phase)

def q_calibration():
    """quadrature point calibration"""
    # Initialize calibration at MCU
    ser.write(bytes([103]))
    # MCU is now collecting data, Get all data:

    measurements = []
    # while True:
    #     print(ser.read(10))
    for i in range(1):
        message = ser.read(2*N_SAMPLES)
        print(i)
        message_bits = BitArray(message)
        for j in range(N_SAMPLES):
            message_bytes = message_bits[0+j*16:(j+1)*16]
            measurements.append(message_bytes.int)

    print("3")

    calculations = []
    for i in range(1):
        message = ser.read(2*N_SAMPLES)
        message_bits = BitArray(message)
        for j in range(N_SAMPLES):
            message_bytes = message_bits[0+j*16:(j+1)*16]
            calculations.append(message_bytes.int)

    print("4")

    time_stamps = []
    for i in range(1):
        message = ser.read(4*N_SAMPLES)
        message_bits = BitArray(message)
        for j in range(N_SAMPLES):
            message_bytes = message_bits[0+j*32:(j+1)*32]
            time_stamps.append(message_bytes.int*0.001)

    # Store all lists as arrays:
    measurements = np.array(measurements)
    calculations = np.array(calculations)
    time_stamps = np.array(time_stamps)

    # Data is collected, perform the fit:

    # make a guess of the frequency
    fft_guess = np.abs(fft.rfft(measurements))

    # Remove DC component and look for max index
    index = np.where(fft_guess[1:] == np.max(fft_guess[1:]))[0]

    fft_freq = fft.rfftfreq(len(measurements), 1/SAMPLE_RATE)
    print("Frequency", index[0], fft_freq[index])

    # Select one of the two freq_init --> if frequency is low just choose 0.1
    # [amp,freq,phase,offset, offset_slope]
    # freq_init = fft_freq[index]
    freq_init = 0
    print(freq_init)
    initial_guess = [0.1,freq_init ,0, 0, 0]
    print("OUTPUT", calculations, measurements)
    plt.figure()
    plt.scatter(time_stamps, measurements)
    plt.show()
    
    # Perform the least squares fit using curve_fit
    optimized_params, _ = curve_fit(sine_func, time_stamps, measurements, p0=initial_guess, maxfev=int(10000))

    # Extract the optimized parameters
    amplitude_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt = optimized_params
    print("Parameters: ", optimized_params)

    # Get the fitted sine 
    sine_fitted = sine_func(time_stamps, amplitude_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt)
    second_derivative_fitted = second_derivative(time_stamps,amplitude_opt,frequency_opt, phase_opt)

    plt.figure()
    plt.scatter(calculations, second_derivative_fitted)
    plt.show()
    # Get guesses of where it is zero
    error = 1000 #0.001 # Adjust error to get more indices, however can be small since it is a fitted sine
    zero_indices = np.where(np.abs(second_derivative_fitted)<error)
    
    # Optimize for roots, again give initial values for correct convergence
    print(time_stamps[zero_indices])
    roots = fsolve(second_derivative, time_stamps[zero_indices], args=(amplitude_opt, frequency_opt, phase_opt))
    roots = np.unique(np.around(roots,decimals=6))
    quad_points = sine_func(roots, amplitude_opt, frequency_opt, phase_opt, offset_opt, offset_slope_opt)
    derivatives = first_derivative(roots, amplitude_opt, frequency_opt, phase_opt, offset_slope_opt)
    slope_signs = np.sign(derivatives)
   

    # Plot the fit
    fig = plt.figure()
    plt.scatter(roots,quad_points,color='purple', marker= 'x')
    plt.scatter(time_stamps, measurements, label='Original Data', marker='.', color= 'cyan')
    plt.plot(time_stamps, sine_fitted,color='red', label='Fitted Curve')
    plt.xlabel("Time [s]")
    plt.ylabel("DC-output Interferometer [V]")
    plt.legend()
    plt.show()

    # Send number of Qpoints to MCU
    n_qpoints = len(quad_points)
    ser.write(n_qpoints)
    print("qpoints send", quad_points)
    
    # Send packets of q points (each packet consists of 2 bytes)
    for i in range(n_qpoints):
        # First get value, then pack into signed short (two bytes), then write to serial as two bytes
        quad_point_value = round(quad_points[i])
        quad_point_bytes = struct.pack('h', quad_point_value)
        ser.write(bytes([quad_point_bytes]))

        roots_value = round(roots[i])
        roots_bytes = struct.pack( roots_value)
        ser.write(bytes([roots_bytes]))

        if slope_signs[i] < 0:
            slope_signs[i] = 0
        ser.write(bytes([slope_signs[i]]))

if __name__ == "__main__":
    print("START")
    # Initialize Serial
    ser = serial.Serial("COM7", baudrate=BAUD_RATE)
    ser.close()
    ser.open()

    while ser.in_waiting:
        print(ser.read())

    handshake()
    # confirm, ser = start_pc_mcu("COM5")

    # Handshake
    #handshake()

    # Do calibration
    q_calibration()
