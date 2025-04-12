import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import sys
import random
import time

# Simulated data generator
def get_fake_lora_data():
    return random.uniform(20, 80) + random.uniform(-1, 1) * time.time() % 1

# App and main window
app = QtWidgets.QApplication(sys.argv)
main_window = QtWidgets.QMainWindow()
main_window.setWindowTitle("Simulated LoRa Live Plot")
main_widget = QtWidgets.QWidget()
main_window.setCentralWidget(main_widget)

# Layouts
layout = QtWidgets.QVBoxLayout()
main_widget.setLayout(layout)

# Plot widget
plot_widget = pg.PlotWidget(title="LoRa Data Stream (Simulated)")
layout.addWidget(plot_widget)
curve = plot_widget.plot()
data = []

# Buttons
button_layout = QtWidgets.QHBoxLayout()
layout.addLayout(button_layout)

start_button = QtWidgets.QPushButton("Start Recording")
stop_button = QtWidgets.QPushButton("Stop Recording")
button_layout.addWidget(start_button)
button_layout.addWidget(stop_button)

# Recording state
recording = False

def update():
    global data
    if recording:
        value = get_fake_lora_data()
        data.append(value)
        curve.setData(data[-100:])  # show last 100 points

def start_recording():
    global recording
    recording = True

def stop_recording():
    global recording
    recording = False

start_button.clicked.connect(start_recording)
stop_button.clicked.connect(stop_recording)

# Timer for updates
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

# Run the GUI
main_window.resize(800, 500)
main_window.show()
sys.exit(app.exec_())
