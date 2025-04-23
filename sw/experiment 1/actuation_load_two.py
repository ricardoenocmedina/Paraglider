import time
import RPi.GPIO as GPIO
import loadcell
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

# Set endianness properly
BYTE_ORDER = Endian.Little
WORD_ORDER = Endian.Big

def parse_motor_response_line(response):
    if response is None or len(response) != 19:
        print("Invalid response length or no response received.")
        return None

    if response[1] != 0x64:
        print(f"Unexpected function code: 0x{response[1]:02X}")
        return None

    pos = int.from_bytes(response[2:6], byteorder='big', signed=True)
    force = int.from_bytes(response[6:10], byteorder='big', signed=True)
    power = int.from_bytes(response[10:12], byteorder='big')
    temp = response[12]
    voltage = int.from_bytes(response[13:15], byteorder='big')
    errors = int.from_bytes(response[15:17], byteorder='big')
    inches = pos/25400

    print(f"pos: {pos:>7} µm | Inches: {inches} in| force: {force:>6} mN | power: {power:>2} W | temp: {temp}°C | voltage: {voltage} mV | errors: 0x{errors:04X}")

    return pos

def setup():
    # Load cell pins
    data_pin1 = 5
    clock_pin1 = 6
    data_pin2 = 7
    clock_pin2 = 8

    loadcell1 = loadcell.init_loadcell(data_pin1, clock_pin1)
    loadcell2 = loadcell.init_loadcell(data_pin2, clock_pin2)

    # Actuator serial ports
    actuator_port1 = '/dev/ttyUSB1'
    actuator_port2 = '/dev/ttyUSB2'

    client1 = ModbusSerialClient(
        method='rtu',
        port=actuator_port1,
        baudrate=19200,
        parity='E',
        stopbits=1,
        bytesize=8,
        timeout=1
    )
    client2 = ModbusSerialClient(
        method='rtu',
        port=actuator_port2,
        baudrate=19200,
        parity='E',
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    return loadcell1, loadcell2, client1, client2

def configure_motion(client, motion_id=0, position_um=120000, duration_ms=10000, delay_ms=100):
    base_addr = 780 + motion_id * 6  # Motion 0 starts at 780, Motion 1 at 786, etc.

    builder = BinaryPayloadBuilder(byteorder=BYTE_ORDER, wordorder=WORD_ORDER)
    builder.add_32bit_int(position_um)
    builder.add_32bit_int(duration_ms)
    builder.add_16bit_uint(delay_ms)
    builder.add_16bit_uint(0x0000)  # No auto-chain

    payload = builder.to_registers()
    client.write_registers(address=base_addr, values=payload, unit=1)

def enter_kinematic_mode(client):
    client.write_register(address=0x0003, value=0x0005, unit=1)  # Set Control Register 3 to mode 5

def trigger_motion(client, motion_id=0):
    client.write_register(address=0x0009, value=motion_id, unit=1)

def set_pid_gains(client, unit_id=1, kp=0.5, ki=0.0, kd=0.0, kp_addr=688, ki_addr=690, kd_addr=692):
    builder = BinaryPayloadBuilder(byteorder=BYTE_ORDER, wordorder=WORD_ORDER)

    builder.add_32bit_float(kp)
    client.write_registers(address=kp_addr, values=builder.to_registers(), unit=unit_id)

    builder.reset()
    builder.add_32bit_float(ki)
    client.write_registers(address=ki_addr, values=builder.to_registers(), unit=unit_id)

    builder.reset()
    builder.add_32bit_float(kd)
    client.write_registers(address=kd_addr, values=builder.to_registers(), unit=unit_id)

if __name__ == "__main__":
    loadcell1, loadcell2, client1, client2 = setup()

    if client1.connect() and client2.connect():
        try:
            set_pid_gains(client1)
            set_pid_gains(client2)

            configure_motion(client1)
            configure_motion(client2)

            enter_kinematic_mode(client1)
            enter_kinematic_mode(client2)

            time.sleep(0.5)

            trigger_motion(client1)
            trigger_motion(client2)

        except Exception as e:
            print(f"Error during actuator operation: {e}")
    else:
        print("Failed to connect to actuator(s).")

    try:
        while True:
            data1 = loadcell.read_loadcell(loadcell1)
            data2 = loadcell.read_loadcell(loadcell2)
            print(f"Load Cell 1: {data1}, Load Cell 2: {data2}")
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        GPIO.cleanup()
