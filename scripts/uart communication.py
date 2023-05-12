import serial

# Configure the serial port
port = serial.Serial('COM5', baudrate=115200, timeout=1) #115200 is default baudrate of esp32

# Open the serial port
if not port.isOpen():
    port.open()

# Send a message over UART
message = b'Hello, world!'
port.write(message)

# Close the serial port
port.close()