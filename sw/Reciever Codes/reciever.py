import serial
import time

ser = serial.Serial('/dev/tty.usbserial-0001', 115200, timeout=1)
time.sleep(2)

def configure_module():
    commands = [
        b'AT+ADDRESS=2\r\n',
        b'AT+BAND=915000000\r\n',
        b'AT+NETWORKID=6\r\n',
        b'AT+PARAMETER=12,7,1,4\r\n'
    ]
    for cmd in commands:
        ser.write(cmd)
        time.sleep(0.2)
        print(">", cmd.decode().strip(),ser.readline().decode().strip())
        # ser.readline()

def extract_message(line):
    """Extract the message from the LoRa response."""
    if line.startswith("+RCV="):
        parts = line.split(",")
        if len(parts) > 2:
            message = parts[2]  # The message is the third element
            return message.strip()
    return None

def listen_for_messages():
    print('Listening for LoRa messages...')

    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                message = extract_message(line)
                if message:
                    print(f'Received: {message}')


if __name__ == "__main__":
    configure_module()
    listen_for_messages()
