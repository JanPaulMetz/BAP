""" Contains class for GUI """
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout,QWidget, QLabel, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

class MainWindow(QMainWindow):
    def __init__(self, update_callback, sweep_callback):
                # frequency_plot_rx, temperature_plot_rx, magnitude_plot_rx,
                #         magnitude_data_updated):
        super().__init__()

        # Update user input
        self.update_callback = update_callback

        # Trigger sweep
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

        # Create text field
        self.text_label = QLabel("Status:")
        self.text_input = QLineEdit()
        self.text_input.setReadOnly(True)
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.text_label)
        text_layout.addWidget(self.text_input)
        self.layout.addLayout(text_layout)

        # Create labels and input fields
        self.freq_labels = []
        self.freq_inputs = []
        self.amp_labels = []
        self.amp_inputs = []

        freq_layout = QHBoxLayout()
        amp_layout = QHBoxLayout()

        for i in range(3):
            freq_label = QLabel("Frequency {}:".format(i + 1))
            freq_input = QLineEdit()
            self.freq_labels.append(freq_label)
            self.freq_inputs.append(freq_input)

            amp_label = QLabel("Amplitude {}:".format(i + 1))
            amp_input = QLineEdit()
            self.amp_labels.append(amp_label)
            self.amp_inputs.append(amp_input)

            freq_layout.addWidget(freq_label)
            freq_layout.addWidget(freq_input)
            amp_layout.addWidget(amp_label)
            amp_layout.addWidget(amp_input)

        self.layout.addLayout(freq_layout)
        self.layout.addLayout(amp_layout)

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
    
    def update_plot(self, omega, magnitudes):
        # Generate x values (time) for the plot
        x = omega

        # Generate y values (amplitude) for the plot
        y = magnitudes

        # Plot the data
        self.axes.clear()
        self.axes.semilogx(x, y)

        # Update the canvas
        self.canvas.draw()
