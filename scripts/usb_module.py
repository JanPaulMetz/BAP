""" This module contains methods for usb handling"""
import sys
import libusb_package       # Needs install of libusb and VS
import usb.core
import usb.backend.libusb1

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
            sys.stdout.write('Device not connected\n')
        return False
    if prnt is True:
        sys.stdout.write('Device is connected\n')
    return True

def print_usb_mouse_input(backend,idvendor,idproduct,packets):
    """print the USB input data got from the defined usb input"""
    device = usb.core.find(backend=backend,idVendor=idvendor,idProduct=idproduct)
    if device is None:
        raise SystemError("Device is not connected")
    endpoint = device[0][(0,0)][0]
    collected = 0
    while collected<packets:
        try:
            data = device.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
            collected += 1
            mouseclick = data[0]
            match(mouseclick):
                case 1:
                    print("Left Mouse Click")
                case 2:
                    print("Right Mouse Click")
                case 4:
                    break
        except usb.core.USBError:
            data = None
            if usb.core.USBError.args == ('Operation timed out',):
                continue

def get_usb_stream(backend,idvendor,idproduct):
    """Get data from the usb device"""
    device = usb.core.find(backend=backend,idVendor=idvendor,idProduct=idproduct)
    if device is None:
        raise SystemError("Device is not connected")
    endpoint = device[0][(0,0)][0]
    while True:
        try:
            data = device.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
            print(data)
        except usb.core.USBError:
            data = None
            if usb.core.USBError.args == ('Operation timed out',):
                continue
