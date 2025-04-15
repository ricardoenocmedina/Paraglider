# script with functions to interface with load cell and amplifier board hx711

# reading raw data from hx711
import time
import board
import busio
import adafruit_hx711
import numpy as np

def getLoadCellData():
    # Create I2C connection
    i2c = busio.I2C(board.SCL, board.SDA)
    hx711 = adafruit_hx711.HX711(i2c, 0x1E, 0x1F)  # Use the correct I2C address for your HX711

    # Set the scale factor (calibration factor) for the load cell
    hx711.set_scale(2280.0)  # Adjust this value based on your calibration

    # Read raw data from the load cell
    raw_data = hx711.read_raw()
    return raw_data

