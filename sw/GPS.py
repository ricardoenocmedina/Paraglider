import serial
import pynmea2
import time

# Set up GPS serial (adjust ttyUSB0 if needed)
gps_serial = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# Set up LoRa serial (adjust ttyUSB1 if needed)
lora_serial = serial.Serial('/dev/ttyUSB1', baudrate=115200, timeout=1)

def send_lora(message):
    command = f"AT+SEND=0,{len(message)},{message}\r\n"
    lora_serial.write(command.encode())
    print(f"Sent over LoRa: {message}")
    time.sleep(2)  # wait for transmission

while True:
    try:
        line = gps_serial.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
            msg = pynmea2.parse(line)

            if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                lat = msg.latitude
                lon = msg.longitude
                gps_data = f"{lat:.6f},{lon:.6f}"
                print(f"GPS: {gps_data}")
                send_lora(gps_data)
                time.sleep(5)  # delay between sends

    except pynmea2.ParseError:
        pass
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
