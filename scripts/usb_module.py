""" This module contains methods for usb handling"""
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
print(list(usb.core.find(find_all=True, backend=libusb1_backend)))

#<DEVICE ID 8086:15ec on Bus 002 Address 000> for the FPGA usb bridge
