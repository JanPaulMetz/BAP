import multiprocessing
import time
from communication_process import Communication

baud_rate = 115200
port = "COM10"
mcu_ready = multiprocessing.Event()
mcu_not_ready = multiprocessing.Event()
update_fpga_rx, update_fpga_tx = multiprocessing.Pipe()


# Create communication
mcu_communication = Communication(baud_rate,port,mcu_ready,mcu_not_ready, update_fpga_rx)

# Begin communication
mcu_communication.serial_begin()

# Handshake
mcu_communication.handshake()

list_to_send = [54,54,32,12]
update_fpga_tx.send(list_to_send)

while True:

    # If there is content in the pipe
    if update_fpga_rx.poll():
        # content_to_send = update_fpga_rx.recv()
        # # GEt id
        # model_id = content_to_send[0]
        # # Get frequencies
        # frequencies = content_to_send[1:7]
        # # Get model params
        # model_params = content_to_send[7:12]
        # # Get amplitudes
        # amplitudes = content_to_send[12:]

        # Send ID
        mcu_communication.led_cmd(True)
        # mcu_communication.model_id(model_id)
        # # Send phasor magnitude
        # mcu_communication.phasor_magnitude(frequencies,model_params,amplitudes)
        # # Update
        # mcu_communication.update_model()
        time.sleep(1)
        mcu_communication.led_cmd(False)
        time.sleep(1)
