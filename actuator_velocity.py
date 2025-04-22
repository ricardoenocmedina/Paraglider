import time
from pymodbus.client import ModbusSerialClient
import struct

def modbus_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')

def build_velocity_command(velocity_um_s):
    """Build a Modbus RTU command to set the actuator's velocity."""
    velocity_bytes = velocity_um_s.to_bytes(4, byteorder='big', signed=True)
    request = bytes([0x01, 0x64, 0x20]) + velocity_bytes  # Command ID for velocity (0x20 assumed)
    crc = modbus_crc(request)
    return request + crc

def move_actuator_velocity(client, velocity_mm_s):
    """
    Move the actuator at a specified velocity until the end.
    velocity_mm_s: Desired velocity in mm/s.
    """
    microns_per_second = int(velocity_mm_s * 1000)  # Convert mm/s to µm/s
    command = build_velocity_command(microns_per_second)
    
    print(f"Sending velocity command: {microns_per_second} µm/s ({velocity_mm_s} mm/s)...")
    client.socket.write(command)
    time.sleep(0.1)
    response = client.socket.read(19)
    print("Response:", response.hex())
    if len(response) == 19:
        parse_motor_response_line(response)
    else:
        print("Incomplete response received.")

def parse_motor_response_line(response):
    if len(response) != 19 or response[1] != 0x64:
        return
    pos = int.from_bytes(response[2:6], byteorder='big', signed=True)
    force = int.from_bytes(response[6:10], byteorder='big', signed=True)
    power = int.from_bytes(response[10:12], byteorder='big')
    temp = response[12]
    voltage = int.from_bytes(response[13:15], byteorder='big')
    errors = int.from_bytes(response[15:17], byteorder='big')
    print(f"pos: {pos:>7} µm | force: {force:>6} mN | power: {power:>2} W | temp: {temp}°C | voltage: {voltage} mV | errors: 0x{errors:04X}")

# Main usage
if __name__ == "__main__":
    client = ModbusSerialClient(
        port='/dev/ttyUSB1',
        baudrate=19200,
        parity='E',
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    if client.connect():
        try:
            while True:
                val = input("Enter velocity in mm/s (or 'q' to quit): ").strip()
                if val.lower() == 'q':
                    break
                try:
                    velocity_mm_s = float(val)
                    move_actuator_velocity(client, velocity_mm_s)
                except ValueError:
                    print("Please enter a valid number.")
        finally:
            client.close()
    else:
        print("Failed to connect to actuator.")
