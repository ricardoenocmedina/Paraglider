# example code from https://github.com/mpibpc-mroose/hx711/ adapted to read 50 kg load cells for paraglider
# last modified: 4/19/25
# author: Alexa


#!/usr/bin/python3
from hx711 import HX711		# import the class HX711
import RPi.GPIO as GPIO		# import GPIO
import time

try:
    DataPin = 6
    ClockPin = 5
    NumReadings = 1

    print("Reading HX711")
    # Create an object hx which represents your real hx711 chip
    # Required input parameters are only 'dout_pin' (data) and 'pd_sck_pin' (clock)
    # If you do not pass any argument 'gain_channel_A' then the default value is 128
    # If you do not pass any argument 'set_channel' then the default value is 'A'
    # you can set a gain for channel A even though you want to currently select channel B
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    
    print("Reset")
    result = hx.reset()		# Before we start, reset the hx711 ( not necessary)
    if result:			# you can check if the reset was successful
        print('Ready to use')
    else:
        print('not ready')
        
    while True:
        # R ead data several, or only one, time and return mean value
        # it just returns exactly the number which hx711 sends
        # argument times is not required default value is 1
        data = hx._read()
        
        if data != False:	# always check if you get correct value or only False
            print('Raw data: ' + str(data))
        else:
            print('invalid data')               

except (KeyboardInterrupt, SystemExit):
    print('Bye :)')
    
finally:
    GPIO.cleanup()


def init_loadcell(data_pin, clock_pin):
    """
    Initialize the load cell.
    
    Args:
        data_pin (int): GPIO pin number for data.
        clock_pin (int): GPIO pin number for clock.
        
    Returns:
        hx (HX711): Initialized HX711 object.
    """
    hx = HX711(dout_pin=data_pin, pd_sck_pin=clock_pin, gain=128, channel='A')
    hx.reset()
    return hx

def read_loadcell(hx, num_readings=1):
    """
    Read data from the load cell.
    
    Args:
        hx (HX711): HX711 object.
        num_readings (int): Number of readings to take.
        
    Returns:
        data (list): List of readings.
    """
    if hx.read():
        data = hx._read(num_readings)
        if data != False:
            return data
        else:
            print('invalid data')