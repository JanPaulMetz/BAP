""" Module containing functions that are used by the process read datastream"""
from bitstring import BitArray

def sync_on_id(data_bits, n_bytes):
    """ SYnc on ID by looking for ID in the data bin
        If found, store the data with ID as first byte
    """
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
    print(data_bits[0:640])
    print(data_bits[640:1280])
    print(data_bits[1280:1920])
    print(data_bits[1920:])
    n_bits = 8*n_bytes
    # package length is 2 bytes
    package_length = 2*8

    message_check_len = 10
     # [t,t,t,t,t ....]
    message_type_expected_time = [BitArray('0b00') for _ in range(message_check_len)]
    # [id, temp, t,t,t,t, ...]
    message_type_expected_id = [BitArray('0b01'), BitArray('0b10')]+ [BitArray('0b00') for _ in range(message_check_len-2)]
    # [temp, t,t,t,t, ..]
    message_type_expected_temp= [BitArray('0b10')] + [BitArray('0b00') for _ in range(message_check_len-1)]
    
    half_package_length = 8
    # flags --> Reset for each increment of j
    message_type_history = []
    empty = []
    for j in range(2):
        # For each 2 bytes one to the right
        print("J", j)
        id_found = False
        unexpected_sequence = False
        message_type_history = empty.copy()
        expected_sequence = False
        for i in range(n_bytes):
            # For each 2 bytes
            message_type = data_bits[package_length*i + j*half_package_length: package_length*i + 2 + j*half_package_length]
            # print("this message", data_bits[package_length*i +j*half_package_length: package_length*i + package_length + j*half_package_length])

            # Check if ID is found
            if message_type == BitArray("0b01"):
                id_found = True
                data_synced = data_bits[package_length*i + j*half_package_length: package_length*i + j*half_package_length + n_bits]
                print("synced data", data_synced)
                # print("data leng", len(data_bits))
                print(package_length*i + j*half_package_length, package_length*i + j*half_package_length + n_bits)
                # print("ID FOUND")
            
            # Perform expectation check
            
            if i > message_check_len:
                history_to_check = message_type_history[i-message_check_len:]
                # print("hist check", history_to_check)
                # If the selected history is as expected (So one of below situations)
           
                # print("ID found",j, id_found)
                print("history", history_to_check)
                for i in range(12):
                    if sequence[i] == history_to_check:
                        print(i)
                        if id_found:
                            print("SYNCED")
                            return id_found, data_synced
                        else:
                            # did not found id
                            expected_sequence = True
                            break

                if not expected_sequence:
                    # Not as expected!
                    unexpected_sequence = True
                    print("Unexpected sequence")

            if unexpected_sequence:
                # If unexpected, break from sequence
                break

            # add to history
            message_type_history.append(message_type)

    # Two tries failed
    print("Failed to sync")
    return False, BitArray(int=0,length=n_bits)
    
def single_point_to_decimal(package_binary):
    """ Convert two's complement to float """
    # If first bit is 1
    # print("error shit", package_binary)
    if package_binary[0] == 1:
        # print(~package_binary)
        decimal = ~package_binary
    
        return -(decimal.uint +1)/(2**len(package_binary))
    else:
        return (package_binary.uint)/(2**len(package_binary))
    