# script to run an experiment where we record load cell and actuator data while actuator pulls on the brake lines

import RPi.GPIO as GPIO
import loadcell
from pymodbus.client import ModbusSerialClient
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
            while True:
                val = input("Enter distance to move in inches (or 'q' to quit): ").strip()
                if val.lower() == 'q':
                    break
                try:
                    inches = float(val)
                    move_actuator.move_actuator_inches(client, inches)
                except ValueError:
                    print("Please enter a valid number.")
        finally:
            client.close()
    else:
        print("Failed to connect to actuator.")

