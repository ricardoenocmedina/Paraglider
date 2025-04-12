#import time
#import board
#import busio
#import adafruit_adxl34x

# Create I2C connection
#i2c = busio.I2C(board.SCL, board.SDA)
#accelerometer = adafruit_adxl34x.ADXL345(i2c)

#def accOutput():
#    while True:
#        x, y, z = accelerometer.acceleration
#        output = f"X: {x:.2f} m/s², Y: {y:.2f} m/s², Z: {z:.2f} m/s²"
#        yield output

#while True:
#    x, y, z = accelerometer.acceleration
#    print(f"X: {x:.2f} m/s², Y: {y:.2f} m/s², Z: {z:.2f} m/s²")
#    time.sleep(0.5)


def accOutput():
    x = 0
    while True:
        x += 1
        output = f"Current number: {x}"
        yield output
