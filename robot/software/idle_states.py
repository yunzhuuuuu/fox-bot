# combines all robot components behavior for the idle state

# return array:
# Serial Data format: (14 byte packet)
# Byte 0 = Speed to set motors to 0-255(byte)
# Bytes 1&2 = Angle delta for robot to move 0-360(2 bytes)
# Byte 3 = Servo angle for ears 0-180(byte), mirrored.
#    face forward: 90, inside: decrease, outside: increase
# Byte 4 = Servo angle for the tail 0-180(byte)
# Bytes 6-13 = Array for the eyes

import time
import random
import struct


class RobotIdleState:

    def __init__(self):
        # initialize robot components
        self.speed = 0  # 0–255
        self.spin = 180  # 0–360
        self.ear = 90  # 0–180
        self.tail = 120  # 0–180
        self.eye_brightness = 1  # for formatting
        self.eye = [0] * 32  # eye array (8 bytes?)

    def build_packet(self):
        """
        Returns EXACT format Arduino expects:
        <B h B B B 8s>   (14 bytes)
        """
        # pack:
        # B   speed
        # h   spin int16
        # B   ear
        # B   tail
        # B   eye brightness
        # 8s  the 8-byte eye array

        # alternative:
        # array[0:3] = bin(fox.speed)[2:]
        # array[4:11] = bin(fox.spin)[2:]
        # array[] ...

        return struct.pack(
            "<BhBBB8B",
            self.speed,
            int(self.spin),
            self.ear,
            self.tail,
            self.eye_brightness,
            *self.eye
        )

    def sleep(self):
        """
        docstring
        """
        self.speed = 0
        self.spin = 0
        self.ear = max(0, self.ear - 2)
        self.tail = min(180, self.tail + 3)
        self.eye = [
            0b00000000,
            0b00000000,
            0b00011000,
            0b00111100,
            0b00111100,
            0b00011000,
            0b00000000,
            0b00000000,
        ]  # hardcoding it for now

    def chase_tail(self):
        """
        docstring
        """
        return None

    # more states

    def run_idle(self):
        # randomly call one of the above states
        behaviors = [self.sleep]  # add self.chase_tail and others when ready
        behavior = random.choice(behaviors)
        return behavior()


if __name__ == "__main__":
    fox = RobotIdleState()
    while True:
        fox.run_idle()
        print(fox.ear)
        array = fox.build_packet()  # array to arduino
        # print(array)
        time.sleep(0.02)  # 50Hz
