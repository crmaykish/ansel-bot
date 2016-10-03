import serial

class MotorBoard:
    UPDATE_RATE = 20    # Rate to run motor updates
    ser = None

    def __init__(self, port, baud, timeout):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        print("Connected to Motor Board.")
    
    def _command(self, command):
        tosend = (command + '\n').encode('ascii')
        self.ser.write(tosend)

    def sleep_time(self):
        return 1 / self.UPDATE_RATE

    def set_movement(self, direction, speed):
        if (speed >= 0 and speed <= 255):
            self._command("d," + direction + "," + speed)

    def stop_movement(self):
        self._command("stop,")