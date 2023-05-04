""" This module contains methods for usb handling"""
import sys
import libusb_package       # Needs install of libusb and VS
import usb.core
import usb.backend.libusb1


libusb1_backend = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
# -> calls usb.libloader.load_locate_library(
#                ('usb-1.0', 'libusb-1.0', 'usb'),
#                'cygusb-1.0.dll', 'Libusb 1',
#                win_cls=win_cls,
#                find_library=find_library, check_symbols=('libusb_init',))
#
# -> calls find_library(candidate) with candidate in ('usb-1.0', 'libusb-1.0', 'usb')
#   returns lib name or path (as appropriate for OS) if matching lib is found

# It would also be possible to pass the output of libusb_package.get_libsusb1_backend()
# to the backend parameter here. In fact, that function is simply a shorthand for the line
# above.
#print(list(usb.core.find(find_all=True, backend=libusb1_backend)))

#<DEVICE ID 8086:15ec on Bus 002 Address 000> for the FPGA usb bridge



# find USB devices
#dev = usb.core.find(find_all=True, backend=libusb1_backend)
# loop through devices, printing vendor and product ids in decimal and hex



def find_all_devices(backend,prnt=False):
    """Find al usb devices connected to computer
    :param backend: USB backend
    :type backend: _Lib_usb
    :param print: If true, prints the devices in the sys.stdout
    (default is False)
    :returns: a list of strings representing the header columns
    :rtype: list"""
    devices = usb.core.find(find_all=True, backend=backend)
    if prnt is True:
        for cfg in devices:
            sys.stdout.write('Decimal VendorID=' +
                            str(cfg.idVendor) +
                            ' & ProductID=' +
                            str(cfg.idProduct) + '\n')
            sys.stdout.write('Hexadecimal VendorID=' +
                            hex(cfg.idVendor)+
                            ' & ProductID=' +
                            hex(cfg.idProduct) + '\n\n')
    return devices

def check_device(backend,idvendor,idproduct,prnt=False):
    """Find USB device with certain vendor id and product id
    :param backend: USB backend
    :param idVendor: Vendor id
    :type idVendor: int
    :param idProduct: Product id
    :type idProduct: int
    :returns: Boolean if device is connected
    rtype: boolean"""
    device = usb.core.find(backend=backend,idVendor=idvendor,idProduct=idproduct)
    if device is None:
        if prnt is True:
            sys.stdout.write('Device not connected')
        return False
    if prnt is True:
        sys.stdout.write('Device is connected')
    return True


ISDEVICECONNECTED = check_device(libusb1_backend,1027,24606,prnt=True)

#devs = find_all_devices(libusb1_backend)
#Decimal VendorID=1027 & ProductID=24606
#Hexadecimal VendorID=0x403 & ProductID=0x601e