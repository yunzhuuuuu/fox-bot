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
import robot.software.eye_display as eye_display


class RobotIdleState:

    def __init__(self):
        # initialize robot components
        self.speed = 0  # 0–255
        self.spin = 180  # 0–360
        self.ear = 90  # 0–180
        self.tail = 120  # 0–180
        self.eye_brightness = 1  # for formatting
        self.eye_object = eye_display.EyeDisplay()
        # self.eye = [0] * 64  # eye array (8 bytes)

        self.last_behavior_end = time.time()
        self.in_idle_behavior = False
        self.behavior = None

        self.chase_tail_phase = 0
        # self.direction = None

    def default(self):
        """
        Passive idle, called when not running a special behavior.

        Slowly reduces movement until static, ears face forward, neutral tail,
        and sets eyes to a centered gaze.
        """
        self.speed = max(0, self.speed - 2)
        self.ear = 90
        self.tail = 120
        # self.eye = [
        #     0b00000000,
        #     0b00000000,
        #     0b00111100,
        #     0b01111110,
        #     0b00111100,
        #     0b00000000,
        #     0b00000000,
        #     0b00000000,
        # ]
        self.eye_object.set_state(self.eye_object.eye_with_position((1, 1)))

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
            int(self.speed),
            int(self.spin),
            int(self.ear),
            int(self.tail),
            self.eye_brightness,
            *self.eye_object.current_state
        )

    def sleep(self):
        """
        Sleep behavior:
        - Ears fold inside
        - Tail curl to the right
        - Eyes show the "sleeping" pattern
        - Runs for 5 seconds before returning to default
        """
        # record the time it starts
        if not hasattr(self, "_behavior_start"):
            self._behavior_start = time.time()

        self.speed = 0
        self.spin = 0
        self.ear = max(0, self.ear - 2)
        self.tail = min(180, self.tail + 3)
        # self.eye = [
        #     0b00000000,
        #     0b00000000,
        #     0b00000000,
        #     0b01100110,
        #     0b00111100,
        #     0b00000000,
        #     0b00000000,
        #     0b00000000,
        # ]  # hardcoding it for now
        self.eye_object.set_state(self.eye_object.sleeping)

        # when finish
        if time.time() - self._behavior_start >= 5.0:  # slept for 5 seconds
            self.in_idle_behavior = False
            self.last_behavior_end = time.time()
            del self._behavior_start

    def chase_tail(self):
        """
        phases:
        - 0. swings the tail to the left, then swings back to the right
        - 1. look at its tail
        - 2. spin to the right, tail moves to the left
        - 3. tail out of sight, gets dizzy
        - 4. cleanup and return to idle

        need to test on robot and adjust all angles and time
        """
        # record the time it starts
        if not hasattr(self, "_behavior_start"):
            self._behavior_start = time.time()
            self.chase_tail_phase = 0
            self.tail = 45
            self._rotate_frames = self.eye_object.eye_rotate(1)  # clockwise
            # print(self._rotate_frames)
            self._frame_index = 0
            self._last_frame_time = None

        now = time.time()
        elapsed = now - self._behavior_start

        # Phase 0: Tail swing
        if self.chase_tail_phase == 0:
            # this should take 0.5 second
            if self.tail <= 120:
                self.tail += (
                    120 - 45
                ) / 50  # 50 time frames in 0.5 seconds under 100Hz
            else:
                self.chase_tail_phase = 1

        # Phase 1: Look at tail
        elif self.chase_tail_phase == 1:
            self.eye_object.set_state(self.eye_object.eye_with_position((3, 2)))
            if elapsed > 0.8:  # look for 0.8 - 0.5 = 0.3 seconds
                self.chase_tail_phase = 2

        # Phase 2: Spin and counter-tail movement
        elif self.chase_tail_phase == 2:
            if elapsed < 2:  # chases its tail for about 2 - 0.5 - 0.3 = 1.2 seconds
                self.spin = min(360, self.spin + 2)
            if elapsed > 1:
                # tail starts to move in opposite direction after 1 second, stops when angle=75
                self.tail = max(75, self.tail - 2)

            if elapsed > 2:
                self.chase_tail_phase = 3
                self._frame_index = 0
                self._last_frame_time = now

        # Phase 3: Dizzy animation
        elif self.chase_tail_phase == 3:
            # Change frames every 0.1s
            if now - self._last_frame_time > 0.1:
                self._last_frame_time = now
                self._frame_index += 1

                if self._frame_index >= len(self._rotate_frames):
                    self.chase_tail_phase = 4
                else:
                    self.eye_object.current_state = self._rotate_frames[
                        self._frame_index
                    ]
                    print(self.eye_object.current_state)

        # Phase 4: End behavior
        if self.chase_tail_phase == 4:
            self.in_idle_behavior = False
            self.last_behavior_end = time.time()
            del self._behavior_start
            del self._rotate_frames
            del self._frame_index
            del self._last_frame_time

        return None

    # more states

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
                behaviors = [
                    self.sleep,
                    self.chase_tail,
                ]  # add self.chase_tail and others when ready
                self.behavior = random.choice(behaviors)
            else:
                # Normal default state
                self.default()


if __name__ == "__main__":
    fox = RobotIdleState()
    # while True:
    #     fox.update()
    #     # print(fox.tail)
    #     array = fox.build_packet()  # array to arduino
    #     print(array)
    #     time.sleep(0.01)  # 100Hz

    # # test
    while True:
        # fox.update()
        fox.chase_tail()
        array = fox.build_packet()
        print(fox.chase_tail_phase)
        print(fox.eye_object.current_state)
