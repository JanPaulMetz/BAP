"""
Python GUI.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class MapWindow(QMainWindow):
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
        self.map_view.load(QUrl("https://www.google.com/maps/"))

        # Create the five buttons
        self.button1 = QPushButton("Button 1", self)
        self.button1.setGeometry(50, 530, 100, 50)

        self.button2 = QPushButton("Button 2", self)
        self.button2.setGeometry(170, 530, 100, 50)

        self.button3 = QPushButton("Button 3", self)
        self.button3.setGeometry(290, 530, 100, 50)

        self.button4 = QPushButton("Button 4", self)
        self.button4.setGeometry(410, 530, 100, 50)

        self.button5 = QPushButton("Button 5", self)
        self.button5.setGeometry(530, 530, 100, 50)

        # Connect the buttons to their respective functions
        self.button1.clicked.connect(self.button1_clicked)
        self.button2.clicked.connect(self.button2_clicked)
        self.button3.clicked.connect(self.button3_clicked)
        self.button4.clicked.connect(self.button4_clicked)
        self.button5.clicked.connect(self.button5_clicked)

    def button1_clicked(self):
        print("Button 1 clicked")

    def button2_clicked(self):
        print("Button 2 clicked")

    def button3_clicked(self):
        print("Button 3 clicked")

    def button4_clicked(self):
        print("Button 4 clicked")

    def button5_clicked(self):
        print("Button 5 clicked")

if __name__ == "__main__":
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create an instance of the MapWindow class
    window = MapWindow()

    # Show the window
    window.show()

    # Start the event loop
    sys.exit(app.exec_())
