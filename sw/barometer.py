# barometer BMP180
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_bitbangio import I2C

dimport board
from adafruit_bitbangio import I2C
from adafruit_bmp3xx import BMP3XX_I2C

def barometer_init():
    # Create software I2C on GPIO D7 (SDA) and D8 (SCL)
    i2c_soft = I2C(scl=board.D8, sda=board.D7)
    
    # Create the BMP3XX object using the I2C bus
    bmp = BMP3XX_I2C(i2c_soft)

    return bmp

'''
returns temperature in Celsius, pressure in hPa, and altitude in meters
'''
def barometer_read(bmp):
    # Read temperature and pressure from the sensor
    temperature = bmp.temperature
    pressure = bmp.pressure
    altitude = bmp.altitude
    return temperature, pressure, altitude
