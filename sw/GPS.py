import serial
import pynmea2
import time

# Set up GPS serial UART connection
gps_serial = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

def getGPS():
    try:
        line = gps_serial.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
            msg = pynmea2.parse(line)

            if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                lat = msg.latitude
                lon = msg.longitude
                return lat, lon

    except pynmea2.ParseError:
        pass
    except Exception as e:
        return -1, -1
    return -1, -1
