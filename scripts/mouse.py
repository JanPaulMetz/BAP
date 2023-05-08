"""Module to read a mouse input array"""
import usb.core
import usb.util
import usb.backend.libusb1
import libusb_package

#Tellegen hall logitech mouse:
#Decimal VendorID=1133 & ProductID=49271
#Hexadecimal VendorID=0x46d & ProductID=0xc077

#initiate USB backend:
libusb1_backend = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
# find the usb device with it's vendor and product id.
dev = usb.core.find(idVendor=1133, idProduct=49271, backend=libusb1_backend)
# first endpoint
endpoint = dev[0][(0,0)][0]
while 1:
    try:
        data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
        mouseclick = data[0]
        match(mouseclick):
            case 1:
                print("Left Mouse Click")
            case 2:
                print("Right Mouse Click")
            case 4:
                break
    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            continue
