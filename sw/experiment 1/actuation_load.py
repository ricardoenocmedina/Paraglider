# script to run an experiment where we record load cell and actuator data while actuator pulls on the brake lines

import RPi.GPIO as GPIO
import loadcell
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import move_actuator


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
        configure_motion(client1, unit_id=1, position_um=120000, duration_ms=10000, delay_ms=100)
        configure_motion(client2, unit_id=1, position_um=120000, duration_ms=10000, delay_ms=100)

        # Trigger both actuators
        trigger_motion(client1, unit_id=1)
        trigger_motion(client2, unit_id=1)
    except Exception as e:
        print(f"Error during actuator operation: {e}")
  else:
    print("Failed to connect to actuator.")

def configure_motion(client, unit_id, position_um, duration_ms, delay_ms):
    # Target position
    builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
    builder.add_32bit_int(position_um)
    payload = builder.to_registers()
    client.write_registers(address=0x030C, values=payload, unit=unit_id)

    # Duration
    builder.reset()
    builder.add_32bit_int(duration_ms)
    payload = builder.to_registers()
    client.write_registers(address=0x030E, values=payload, unit=unit_id)

    # Delay
    client.write_register(address=0x0310, value=delay_ms, unit=unit_id)

    # Disable chaining
    client.write_register(address=0x0311, value=0x0000, unit=unit_id)

def trigger_motion(client, motion_id=0):
    client.write_register(address=0x0009, value=motion_id, unit=unit_id)
