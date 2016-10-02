# Ansel Sensor Board - Colin Maykish - September 2016
import serial
import time
import sqlite3
import json
from threading import Thread

sensors = None

# Set up SQLite database
conn = sqlite3.connect("db/ansel.db")
c = conn.cursor()

# Send a command to a serial device
def command(board, command):
    tosend = (command + '\n').encode('ascii')
    board.write(tosend)

def sensor_check(direction, distance):
    return sensors[direction]['val'] < distance and sensors[direction]['val'] != 0

def sensor_loop():
    sensor_board = serial.Serial("/dev/ttyUSB1", 9600, timeout=10)
    print("Connected to Sensor Board")
    while True:
        try:
            reading = sensor_board.readline().decode("utf-8")
            json_dict = json.loads(reading)
            global sensors
            sensors = json_dict['sensors']
        except UnicodeDecodeError:
            print("Bad data from serial")
        except ValueError:
            print("JSON parsing error")

def control_loop():
    drive_board = serial.Serial("/dev/ttyUSB0", 115200, timeout=10)
    print("Connected to Drive Board")
    
    # Don't start driving until the sensor readings are coming in
    while(sensors is None):
        continue
    
    print("Starting to drive")
    while True:
        if sensor_check(0, 30) or sensor_check(1, 20) or sensor_check(9, 20):
            # Too close to something
            if sensors[9] == 0:
                # Left is wide open
                command(drive_board, "d,left,190")
            elif sensors[1]['val'] == 0:
                # Right is wide open
                command(drive_board, "d,right,190")
            elif sensors[9]['val'] > sensors[1]['val']:
                # Left has more room than right
                command(drive_board, "d,left,190")
            else:
                # Right has more room then left (or they're the same)
                command(drive_board, "d,right,190")

                # TODO: room for improvement here
        else:
            # Nothing blocking, move forward
            command(drive_board, "d,forward,255")

        # 25 updates per second
        time.sleep(0.04)

# Start the sensor board thread
sensor_thread = Thread(target=sensor_loop)
sensor_thread.start()

# Start the main drive control loop
control_loop()