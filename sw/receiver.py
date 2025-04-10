import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

print("Waiting for LoRa messages...")

while True:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("+RCV"):
            print(f"Received: {line}")
