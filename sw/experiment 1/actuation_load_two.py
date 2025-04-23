import time
import RPi.GPIO as GPIO
import loadcell
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import transmitter

# Set endianness properly
BYTE_ORDER = Endian.Little
WORD_ORDER = Endian.Big

def setup():
    # LoRa setup
    transmitter.configure_module()
    transmitter.send_message('Setup complete')

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

def actuator_data(client):
    actuator_data = client.socket.read(19)
    pos = int.from_bytes(actuator_data[2:6], byteorder='big', signed=True)
    force = int.from_bytes(actuator_data[6:10], byteorder='big', signed=True)
    power = int.from_bytes(actuator_data[10:12], byteorder='big', signed=True)
    temp = actuator_data[12]
    voltage = int.from_bytes(actuator_data[13:15], byteorder='big', signed=True)
    errors = actuator_data[15:17]
    return pos, force, power

if __name__ == "__main__":
    loadcell1, loadcell2, client1, client2 = setup()
    '''
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
        '''
    # Send actuator data and load cell data to LoRa receiver
    pos1, force1, power1 = actuator_data(client1)
    pos2, force2, power2 = actuator_data(client2)

    loadcell1_data = loadcell.read_loadcell(loadcell1)
    loadcell2_data = loadcell.read_loadcell(loadcell2)

    message = f'{pos1}, {force1}, {power1}, {loadcell1_data}, {pos2}, {force2}, {power2}, {loadcell2_data}'
    transmitter.send_message(message)
    print("Data sent:", message)

def parse_raspi_data(message):
    # message     message = f'{pos1}, {force1}, {power1}, {loadcell1_data}, {pos2}, {force2}, {power2}, {loadcell2_data}'
