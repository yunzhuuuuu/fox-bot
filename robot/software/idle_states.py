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
        self.eye = [0] * 64  # eye array (8 bytes)

        self.last_behavior_end = time.time()
        self.in_idle_behavior = False
        self.behavior = None

    def default(self):
        self.speed = max(0, self.speed - 2)
        self.ear = 90
        self.tail = 120
        self.eye = [
            0b00000000,
            0b00000000,
            0b00111100,
            0b01111110,
            0b00111100,
            0b00000000,
            0b00000000,
            0b00000000,
        ]

    def build_packet(self):
        """
        Returns 14-byte format Arduino expects:
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
        # record the time it starts
        if not hasattr(self, "_behavior_start"):
            self._behavior_start = time.time()

        self.speed = 0
        self.spin = 0
        self.ear = max(0, self.ear - 2)
        self.tail = min(180, self.tail + 3)
        self.eye = [
            0b00000000,
            0b00000000,
            0b00000000,
            0b01100110,
            0b00111100,
            0b00000000,
            0b00000000,
            0b00000000,
        ]  # hardcoding it for now

        # when finish
        if time.time() - self._behavior_start >= 5.0:  # slept for 5 seconds
            self.in_idle_behavior = False
            self.last_behavior_end = time.time()
            del self._behavior_start

    def chase_tail(self):
        """
        docstring
        """

        return None

    # more states

    # def run_idle(self):
    #     # randomly call one of the above states
    #     behaviors = [self.sleep]  # add self.chase_tail and others when ready
    #     behavior = random.choice(behaviors)
    #     return behavior()

    def update(self):
        """
        Called every time frame. Handles:
        - Starting idle behavior every 10 sec
        - Running idle behavior for 5 sec
        - Returning to default() after that
        """

        now = time.time()

        if self.in_idle_behavior:
            self.behavior()

        else:
            # Default state until it's time to start a behavior
            if now - self.last_behavior_end >= 10.0:
                self.in_idle_behavior = True
                behaviors = [self.sleep]  # add self.chase_tail and others when ready
                self.behavior = random.choice(behaviors)
            else:
                # Normal default state
                self.default()


if __name__ == "__main__":
    fox = RobotIdleState()
    while True:
        fox.update()
        # print(fox.tail)
        array = fox.build_packet()  # array to arduino
        print(array)
        time.sleep(0.5)  # 50Hz
