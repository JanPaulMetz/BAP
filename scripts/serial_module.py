"""Module to write to serial connection"""
import serial


def serial_init(comp):
    """Initialize serial port"""
    ser = serial.Serial(port=comp,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE)
    return ser

def serial_write(port,message):
    """write on serial port"""
    port.write(message)

def serial_read(port):
    """Read on the serial port"""
    serial_message = port.read()
    #read_line = port.readline()
    #serial_message = read_line.decode().replace('\n','')
    return serial_message.hex()

def check_buffer_content(port):
    """Check if the buffer is empty
    returns amount of waiting bits"""
    port.read_all()
    return port.in_waiting
