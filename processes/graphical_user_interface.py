import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import numpy as np
import threading
import time


class MainWindow(QMainWindow):
    def __init__(self, update_callback, sweep_callback):
        super().__init__()

        self.update_callback = update_callback
        self.sweep_callback = sweep_callback

        # Set window title
        self.setWindowTitle("GUI Example")

        # Create main widget and layout
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        # Create plot figure and axes
        self.figure = plt.figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Amplitude")

        # Create plot canvas
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)

        # Create labels and input fields
        self.freq_labels = []
        self.freq_inputs = []
        self.amp_labels = []
        self.amp_inputs = []

        for i in range(3):
            freq_label = QLabel("Frequency {}:".format(i + 1))
            freq_input = QLineEdit()
            self.freq_labels.append(freq_label)
            self.freq_inputs.append(freq_input)

            amp_label = QLabel("Amplitude {}:".format(i + 1))
            amp_input = QLineEdit()
            self.amp_labels.append(amp_label)
            self.amp_inputs.append(amp_input)

            self.layout.addWidget(freq_label)
            self.layout.addWidget(freq_input)
            self.layout.addWidget(amp_label)
            self.layout.addWidget(amp_input)

        # Create buttons
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_button_clicked)
        self.layout.addWidget(self.update_button)

        self.sweep_button = QPushButton("Sweep")
        self.sweep_button.clicked.connect(self.sweep_button_clicked)
        self.layout.addWidget(self.sweep_button)

        # Set the main widget
        self.setCentralWidget(self.main_widget)

    def update_button_clicked(self):
        # Call the update callback with the new values
        frequencies = [self.get_float_value(input_field.text()) for input_field in self.freq_inputs]
        amplitudes = [self.get_float_value(input_field.text()) for input_field in self.amp_inputs]
        self.update_callback(frequencies, amplitudes)

    def sweep_button_clicked(self):
        # Call the sweep callback
        self.sweep_callback()

    def get_float_value(self, text):
        try:
            return float(text)
        except ValueError:
            return 0.0

    def update_plot(self, frequencies, amplitudes):
        # Generate x values (time) for the plot
        x = np.linspace(0, 1, 1000)

        # Generate y values (amplitude) for the plot
        y = sum([amplitude * np.sin(2 * np.pi * frequency * x) for frequency, amplitude in zip(frequencies, amplitudes)])

        # Plot the data
        self.axes.clear()
        self.axes.plot(x, y)

        # Update the canvas
        self.canvas.draw()


def update_plot(window):
    while True:
        # Update the plot based on the variables in main
        window.update_plot(frequencies, amplitudes)
        # Sleep for a certain interval
        time.sleep(1)



def main():
    # Set initial values
    frequencies = [0.0, 0.0, 0.0]
    amplitudes = [0.0, 0.0, 0.0]

    def update_callback(new_frequencies, new_amplitudes):
        nonlocal frequencies, amplitudes
        frequencies = new_frequencies
        amplitudes = new_amplitudes

    def sweep_callback():
        print("Frequency sweep initiated.")
    
    # Create the application
    app = QApplication(sys.argv)

    # Create the main window
    window = MainWindow(update_callback=update_callback, sweep_callback=sweep_callback)

    # Start a separate thread to continuously update the plot
    update_thread = threading.Thread(target=update_plot)
    update_thread.daemon = True
    update_thread.start()

    # Show the main window
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
