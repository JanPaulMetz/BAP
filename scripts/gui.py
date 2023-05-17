"""
Python GUI.
"""
import sys
from time import sleep
from startup_pc_mcu import start_pc_mcu

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

COMPORT = "COM5"

def stop_button():
    """read if the stop button is clicked"""
    #read stop_button from user interface
    clicked = False
    return clicked

class MapWindow(QMainWindow):
    """Making a GUI"""
    def __init__(self):
        super().__init__()

        # Initialize the window settings
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Live Map")

        # Create a widget to hold the map view
        self.map_widget = QWidget(self)
        self.map_widget.setGeometry(0, 0, 800, 500)

        # Create a QWebEngineView object to show the map
        self.map_view = QWebEngineView(self.map_widget)
        self.map_view.setGeometry(0, 0, 800, 500)
        self.map_view.load(QUrl("https://ishettijdvoorbier.com/"))

        # Create the five buttons
        self.button1 = QPushButton("STOP", self)
        self.button1.setGeometry(50, 530, 100, 50)

        self.button2 = QPushButton("START", self)
        self.button2.setGeometry(170, 530, 100, 50)

        self.button3 = QPushButton("Button 3", self)
        self.button3.setGeometry(290, 530, 100, 50)

        self.button4 = QPushButton("Button 4", self)
        self.button4.setGeometry(410, 530, 100, 50)

        self.button5 = QPushButton("Button 5", self)
        self.button5.setGeometry(530, 530, 100, 50)

        # Connect the buttons to their respective functions
        self.button1.clicked.connect(self.stop_button_clicked)
        self.button2.clicked.connect(self.start_button_clicked)
        self.button3.clicked.connect(self.button3_clicked)
        self.button4.clicked.connect(self.button4_clicked)
        self.button5.clicked.connect(self.button5_clicked)

    #Button methods
    #TODO: FPGA AND MCU HANDLING TO STOP
    def stop_button_clicked(self):
        """If stop button is pressed, the program will exit"""
        sys.exit()

    def start_button_clicked(self):
        """Startup button to start startup sequence"""
        max_attempts = 10
        count = 0
        
        print("Button 2 clicked")
        while check_buffer_content() is not None:
            sleep(0.1)

        while count<max_attempts:
            send_mcu_start_message(COMPORT)
            return_message = get_mcu_confirmation(COMPORT)
            if return_message is not None:
                break
            count += 1
        if return_message is None:
            print("Could not establish connection with MCU.")
            sys.exit()
        elif return_message == "start":   #TODO: change start message.
            print("Connection established")
            return
        else:
            print("that was not the message we expected, aborting")
            sys.exit()

    def button3_clicked(self):
        print("Button 3 clicked")
        

    def button4_clicked(self):
        print("Button 4 clicked")

    def button5_clicked(self):
        print("Button 5 clicked")

if __name__ == "__main__":
    # Create a QApplication instance
    start_pc_mcu(COMPORT)
    app = QApplication(sys.argv)

    # Create an instance of the MapWindow class
    window = MapWindow()

    # Show the window
    window.show()

    # Start the event loop
    sys.exit(app.exec_())
