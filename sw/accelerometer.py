import time
import board
import busio
import adafruit_adxl34x

# Create I2C connection
i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)
accelerometer.set_data_rate(100)  # Set data rate to 100 Hz

def getAcceleration():
    x, y, z = accelerometer.acceleration
    return x, y, z        
        
def getRawAcceleration():
    x, y, z = accelerometer.raw_acceleration
    return x, y, z