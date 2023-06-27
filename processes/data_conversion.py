from math import ceil
import struct

import numpy as np

FP_SIZE = 16
FP_DATA_BYTES = ceil(FP_SIZE/8)
POLY_DIM = 10
EXTRA_DIM = 5
FREQ_DIM = 3
cmd = { "set_led": 0b01100001,
        "request_amplitude": 0b01100010,
        "param_frequencies": 0b01100011,
        "param_polynomial_features": 0b01100100,
        "param_extra_feature": 0b01100101,
        "param_magnitude_weights": 0b01100110,
        "param_phase_weights": 0b01100111,
        "param_phasor_magnitude": 0b01101000,
        "param_phasor_phase": 0b01101001,
        "param_model_id": 0b01101010
        }

frequencies = [0x180002AA, 0x300002AA, 0x100002AA]                  # 32 bit unsigned (Phase increase per clk cycle where 2^32 is 2*pi increase)
polynomial_features = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                       [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]     # FP_SIZE bit float
extra_feature = [1]                                               # FP_SIZE bit float
magnitude_weights = [3*i for i in range(0, POLY_DIM*EXTRA_DIM)]       # FP_SIZE bit float
phase_weights = [1*i for i in range(0, POLY_DIM*EXTRA_DIM)]         # FP_SIZE bit float
phasor_magnitude = [1000, 4000, 13000]                               # FP_SIZE bit float (Value between -2^15 to 2^15 -1)
phasor_phase = [2, 1, 1.5]                                   # FP_SIZE bit float (Value between 0 to 2*pi)
model_id = [1248]                                                   # 14 bit unsigned (sent as 16 bits)


def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def std_logic_vector(value, size):
    assert value < 2 ** size
    return '"' + format(value, '0'+str(size)+'b') + '"'


def to_bytes(data, byte_count=FP_DATA_BYTES):
    fmt = { 1: "B",
            2: 'H',
            4: 'I',
            8: 'Q'}
    assert byte_count in fmt.keys()
    return list(struct.unpack(str(byte_count)+'B', struct.pack('>'+fmt[byte_count], data)))


def make_cmd_array(command, data_list, data_byte_count=FP_DATA_BYTES):
    byte_list = flatten([to_bytes(i, data_byte_count) for i in data_list])
    return "({}, {})".format(std_logic_vector(command, 8), ", ".join([std_logic_vector(i, 8) for i in byte_list])), len(byte_list)+1


def float_to_hex(value, size):
    if size == 16:
        return np.float16(value).view(np.int16)
    elif size == 32:
        return np.float32(value).view(np.int32)
    else:
        raise Exception("parameter size not 16 or 32 : " + str(size))


def print_tb_arrays():
    byte_count = 0
    print("type variable_array is array (natural range <>) of std_logic_vector(7 downto 0);")

    # Send param_frequencies
    cmds, length = make_cmd_array(cmd["param_frequencies"], flatten(frequencies), data_byte_count=4)
    byte_count += length
    print("-- frequencies =", str(frequencies))
    print("constant frequencies_cmds: variable_array(FREQ_DIM*" + str(4) + " downto 0) :=", cmds, ";")

    # Send param_polynomial_features
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(polynomial_features)]
    cmds, length = make_cmd_array(cmd["param_polynomial_features"], raw_data)
    byte_count += length
    print("-- polynomial_features =", str(polynomial_features))
    print("constant polynomial_features_cmds: variable_array(FREQ_DIM*POLY_DIM*" + str(FP_DATA_BYTES) + " downto 0) :=", cmds, ";")

    # Send param_extra_feature
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(extra_feature)]
    cmds, length = make_cmd_array(cmd["param_extra_feature"], raw_data)
    byte_count += length
    print("-- extra_feature =", str(extra_feature))
    print("constant extra_feature_cmds: variable_array(" + str(FP_DATA_BYTES) + " downto 0) :=", cmds, ";")

    # Send param_magnitude_weights
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(magnitude_weights)]
    cmds, length = make_cmd_array(cmd["param_magnitude_weights"], raw_data)
    byte_count += length
    print("-- magnitude_weights =", str(magnitude_weights))
    print("constant magnitude_weights_cmds: variable_array(EXTRA_DIM*POLY_DIM*" + str(FP_DATA_BYTES) + " downto 0) :=", cmds, ";")

    # Send param_phase_weights
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(phase_weights)]
    cmds, length = make_cmd_array(cmd["param_phase_weights"], raw_data)
    byte_count += length
    print("-- phase_weights =", str(phase_weights))
    print("constant phase_weights_cmds: variable_array(EXTRA_DIM*POLY_DIM*" + str(FP_DATA_BYTES) + " downto 0) :=", cmds, ";")

    # Send param_phasor_magnitude
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(phasor_magnitude)]
    cmds, length = make_cmd_array(cmd["param_phasor_magnitude"], raw_data)
    byte_count += length
    print("-- phasor_magnitude =", str(phasor_magnitude))
    print("constant phasor_magnitude_cmds: variable_array(FREQ_DIM*" + str(FP_DATA_BYTES) + " downto 0) :=", cmds, ";")

    # Send param_phasor_phase
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(phasor_phase)]
    cmds, length = make_cmd_array(cmd["param_phasor_phase"], raw_data)
    byte_count += length
    print("-- phasor_phase =", str(phasor_phase))
    print("constant phasor_phase_cmds: variable_array(FREQ_DIM*" + str(FP_DATA_BYTES) + " downto 0) :=", cmds, ";")

    # Send param_model_id
    cmds, length = make_cmd_array(cmd["param_model_id"], flatten(model_id), data_byte_count=2)
    byte_count += length
    print("-- model_id =", str(model_id))
    print("constant model_id_cmds: variable_array(2 downto 0) :=", cmds, ";")

    return byte_count


if __name__ == "__main__":

    # poly features
    raw_data = [float_to_hex(a, FP_SIZE) for a in flatten(polynomial_features)]
    b_arr = bytes([cmd['set_led']] + flatten([to_bytes(i, 2) for i in raw_data]))

    print(type(flatten([to_bytes(i, 2) for i in raw_data])))
    # b_arr_message = bytes(flatten([to_bytes(i, 2) for i in raw_data]))
    # Print actual bytes
    print (''.join(format(x, '02x') for x in b_arr))