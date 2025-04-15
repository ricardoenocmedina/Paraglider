
# transmitter.py

import serial
import time
from accelerometer import accOutput

# Initialize serial port for the USB-TTL adapter
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Allow module to initialize

# Optional: Configure LoRa module
def configure_module():
    commands = [
        b'AT+ADDRESS=1\r\n',
        b'AT+BAND=915000000\r\n',
        b'AT+NETWORKID=6\r\n',
        b'AT+PARAMETER=12,7,1,4\r\n'
    ]
    for cmd in commands:
        ser.write(cmd)
        print(">", cmd.decode().strip(), ser.readline().decode().strip())

# Send a test message to receiver at address 2
def send_message():
    # msg = "Ricardo Medina"
    msg = accOutput()
    for data in msg:
        command = f"AT+SEND=2,{len(data)},{data}\r\n"
        ser.write(command.encode())
        print("Sent:", data)
    # print(type(msg))

if __name__ == "__main__":
    configure_module()
    send_message()
