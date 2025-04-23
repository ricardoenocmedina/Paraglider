
import time
import struct
from pymodbus.client import ModbusSerialClient

DEVICE_ADDRESS = 0x01
FUNCTION_CODE = 0x64
SUBFUNCTION_CODE = 0x1E  # Position Control Stream
TIMEOUT_MS = 500  # Motor communication timeout

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

def build_position_stream_command(position_um):
    position_bytes = position_um.to_bytes(4, byteorder='big', signed=True)
    request = bytes([DEVICE_ADDRESS, FUNCTION_CODE, SUBFUNCTION_CODE]) + position_bytes
    crc = modbus_crc(request)
    return request + crc

def parse_motor_response_line(response):
    if len(response) != 19 or response[1] != 0x64:
        print("Invalid response format.")
        return
    pos = int.from_bytes(response[2:6], byteorder='big', signed=True)
    force = int.from_bytes(response[6:10], byteorder='big', signed=True)
    power = int.from_bytes(response[10:12], byteorder='big')
    temp = response[12]
    voltage = int.from_bytes(response[13:15], byteorder='big')
    errors = int.from_bytes(response[15:17], byteorder='big')
    print(f"pos: {pos:>7} µm | force: {force:>6} mN | power: {power:>2} W | temp: {temp}°C | voltage: {voltage} mV | errors: 0x{errors:04X}")

def move_with_velocity(client, velocity_mm_s, duration_s):
    velocity_um_s = int(velocity_mm_s * 1000)
    step_interval = 0.1  # 100ms interval
    steps = int(duration_s / step_interval)
    current_position = 0  # initial position in µm

    print(f"Starting motion at {velocity_mm_s} mm/s for {duration_s} seconds...")
    for _ in range(steps):
        current_position += int(velocity_um_s * step_interval)
        command = build_position_stream_command(current_position)
        client.socket.write(command)
        time.sleep(0.01)  # brief wait before read
        response = client.socket.read(19)
        if response:
            parse_motor_response_line(response)
        time.sleep(step_interval - 0.01)

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
                    velocity = float(val)
                    duration = float(input("Enter duration in seconds: ").strip())
                    move_with_velocity(client, velocity, duration)
                except ValueError:
                    print("Invalid input.")
        finally:
            client.close()
    else:
        print("Failed to connect to actuator.")
