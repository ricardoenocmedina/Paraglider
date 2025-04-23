# script to run an experiment where we record load cell and actuator data while actuator pulls on the brake lines

import RPi.GPIO as GPIO
import loadcell
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


def setup():
  # load cell pins
  data_pin1 = 5
  clock_pin1 = 6
  data_pin2 = 7
  clock_pin2 = 8

  loadcell1 = loadcell.init_loadcell(data_pin1, clock_pin1)
  loadcell2 = loadcell.init_loadcell(data_pin2, clock_pin2)

  # actuator pins
  actuator_port1 = '/dev/ttyUSB1'
  actuator_port2 = '/dev/ttyUSB2'

  client1 = ModbusSerialClient(
        port= actuator_port1,
        baudrate=19200,
        parity='E',
        stopbits=1,
        bytesize=8,
        timeout=1
    )
  client2 = ModbusSerialClient(
        port= actuator_port2,
        baudrate=19200,
        parity='E',
        stopbits=1,
        bytesize=8,
        timeout=1
    )

  if client1.connect() and client2.connect():
    try:
        # Set PID gains for both actuators
        set_pid_gains(client1, unit_id=1, kp=0.5, ki=0.0, kd=0.0)
        set_pid_gains(client2, unit_id=1, kp=0.5, ki=0.0, kd=0.0)
        
        configure_motion(client1, unit_id=1, position_um=120000, duration_ms=10000, delay_ms=100)
        configure_motion(client2, unit_id=1, position_um=120000, duration_ms=10000, delay_ms=100)

        # Trigger both actuators
        trigger_motion(client1, unit_id=1)
        trigger_motion(client2, unit_id=1)
    except Exception as e:
        print(f"Error during actuator operation: {e}")
  else:
    print("Failed to connect to actuator.")

  return loadcell1, loadcell2, client1, client2

def configure_motion(client, unit_id, end_position_um, duration_ms, delay_ms):
    # Set end target position to KIN_MOTION_0 (registers 0x030C and 0x030D)
    builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
    builder.add_32bit_int(end_position_um)
    position_payload = builder.to_registers()
    client.write_registers(address=0x030C, values=position_payload, unit=unit_id)

    # Set duration (0x030E and 0x030F)
    builder.reset()
    builder.add_32bit_int(duration_ms)
    duration_payload = builder.to_registers()
    client.write_registers(address=0x030E, values=duration_payload, unit=unit_id)

    # Set delay to 100 ms (0x0310)
    client.write_register(address=0x0310, value=100, unit=unit_id)

    # Disable chaining and autostart (0x0311 = 0x0000)
    client.write_register(address=0x0311, value=0x0000, unit=unit_id)

def trigger_motion(client, motion_id=0):
    client.write_register(address=0x0009, value=motion_id, unit=client)

def set_pid_gains(client, unit_id=1, kp=1.0, ki=0.0, kd=0.0, kp_addr=688, ki_addr=690, kd_addr=692):

    builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)

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
    try:
        while True:
            # Read load cell data
            loadcell1_data = loadcell.read_loadcell(loadcell1)
            loadcell2_data = loadcell.read_loadcell(loadcell2)

            # Print or log the data
            print(f"Load Cell 1: {loadcell1_data}, Load Cell 2: {loadcell2_data}")

    except KeyboardInterrupt:
        print("Stop")
    finally:
        GPIO.cleanup()
