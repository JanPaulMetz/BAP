"""startup procedure fsm for the pc"""
import serial_module

def get_mcu_confirmation(comp):
    """checks if mcu send a confirmation message back
    returns the return message or none if no communication was possible. 
    """
    # Try "MAX_COUNT" times to read from serial
    max_count = 5
    count = 0
    while count<max_count:
        return_message = serial_module.serial_read(comp)
        if return_message is None:
            count += 1
        else:
            break
    return return_message

def send_mcu_start_message(comp):
    """"sends start message to MCU"""
    startmessage = "start"
    serial_module.serial_write(comp,startmessage)

    # If not succesful

    # STATE = NEW_STATE
    # if RESET == 1:
    #     STATE = 0
    # else:
    #     match STATE:
    #         case 0:
    #             print("state 0")
    #             if START_BUTTON_PRESSED:
    #                 NEW_STATE = 1
    #             else: 
    #                 NEW_STATE = 0
    #         case 1:
    #             print("state 1")
    #             send_start_message() #send start message to MCU
    #             NEW_STATE = 2
    #         case 2:
    #             print("state 2")
    #             message = read_serial()
    #             if message is None:
    #                 COUNTER += 1
    #                 NEW_STATE = STATE
    #             elif message == STARTMESSAGE
    #         case _:
    #             print("no state detected, system will reset")
    #             RESET = 1
