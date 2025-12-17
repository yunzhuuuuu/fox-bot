# combines all robot components behavior for the idle state

# return array:
# Serial Data format: (21 byte packet)
# Byte 0&1 = Speed to set left&right motors to (-127)-(128)(byte)
# Byte 2 = Servo angle for ears 0-180(byte), mirrored.
#    face forward: 90, inside: decrease, outside: increase
# Byte 3 = Servo angle for the tail 0-120(byte)
# Byte 4 = Brightness of the eyes (0-1)
# Bytes 5-12 = Array for the left eye
# Bytes 13-20 = Array for the right eye


import struct
import math
from enum import IntEnum
import robot.software.eye_display as eye_display
from robot.software.berry_detection import BerryDetection


class Parameters(IntEnum):
    TAIL_LOW = 0
    TAIL_HIGH = 120
    TAIL_MID = 60
    TAIL_DEFAULT = 100
    EAR_LOW = 90
    EAR_HIGH = 180
    EAR_DEFAULT = 140
    SPEED_LOW = 30
    SPEED_HIGH = 45

class RobotBehaviors:

    def __init__(self, manager):

        # initialize robot components
        self.left_speed = 0  # -128 - 127
        self.right_speed = 0  # -128 - 127
        self.ear = Parameters.EAR_DEFAULT  # 0–180
        self.tail = Parameters.TAIL_DEFAULT  # 0–120
        self.eye_brightness = 1  # for formatting
        self.left_eye = eye_display.EyeDisplay()
        self.right_eye = eye_display.EyeDisplay()
        # self.eye = [0] * 64  # eye array (8 bytes)
        self.left_eye.set_state(self.left_eye.eye_with_position((1, 1)))
        self.right_eye.set_state(self.right_eye.eye_with_position((2, 1)))

        self.manager = manager
        self.state = self.manager.state
        self.behavior = self.default

        self.berry_detection = BerryDetection()

        self._wag_direction = 1  # 1 = increasing, -1 = decreasing
        self._ear_direction = 1

        self._left_rotate_frames = self.left_eye.eye_rotate(1)  # clockwise
        self._right_rotate_frames = self.right_eye.eye_rotate(0)  # counterclock

    def update_behavior(self):
        self.state = self.manager.state
        match self.state:
            case "run_petted":
                self.behavior = lambda: self.petted(self.manager.eye_state)
            case "run_look_for_treat":
                elapsed = self.manager.now - self.manager.look_for_treat_start
                self.behavior = lambda: self.look_for_treat(elapsed)
            case "run_sleep":
                self.behavior = self.sleep
            case "blink":
                elapsed = self.manager.now - self.manager.idle_start
                self.behavior = lambda: self.blink(elapsed)
            case "chase_tail":
                elapsed = self.manager.now - self.manager.idle_start
                self.behavior = lambda: self.chase_tail(elapsed)
            case "wag_tail":
                self.behavior = self.wag_tail
            case "look_around":
                elapsed = self.manager.now - self.manager.idle_start
                self.behavior = lambda: self.look_around(elapsed)
            case _:
                self.behavior = self.default

    def build_packet(self):
        """
        Returns 21-byte format Arduino expects:
        <bb B B B 8s 8s>
        L  R  ear tail bright  leftEye  rightEye
        """
        # pack:
        # [0]   left motor  (0-255, reformatted from -127-128)
        # [1]   right motor (0-255, reformatted from -127-128)
        # [2]   ear servo   (0-180)
        # [3]   tail servo  (0-120)
        # [4]   eye brightness (0-1 → scaled to 0–255)
        # [5-12]   left eye  8 bytes
        # [13-20]  right eye 8 bytes
        return struct.pack(
            "<BBBBB8B8B",
            int(self.left_speed + 127),
            int(self.right_speed + 127),
            int(self.ear),
            int(self.tail),
            self.eye_brightness,
            *self.left_eye.current_state,
            *self.right_eye.current_state,
        )

    def default(self):
        """
        Passive idle, called when not running a special behavior.

        Slowly reduces movement until static, ears face forward, neutral tail,
        and sets eyes to a centered gaze.
        """
        if self.left_speed < 0:
            self.left_speed = min(0, self.left_speed + 2)
        elif self.right_speed < 0:
            self.right_speed = min(0, self.right_speed + 2)
        elif self.left_speed > 0:
            self.left_speed = max(0, self.left_speed - 2)
        elif self.right_speed > 0:
            self.right_speed = max(0, self.right_speed - 2)

        if self.ear < Parameters.EAR_DEFAULT:
            self.ear = min(self.ear + 2, Parameters.EAR_DEFAULT)
        elif self.ear > Parameters.EAR_DEFAULT:
            self.ear = max(self.ear - 2, Parameters.EAR_DEFAULT)
        self.ear = max(0, min(180, self.ear))

        if self.tail < Parameters.TAIL_DEFAULT:
            self.tail = min(self.tail + 2, Parameters.TAIL_DEFAULT)
        elif self.tail > Parameters.TAIL_DEFAULT:
            self.tail = max(self.tail - 2, Parameters.TAIL_DEFAULT)
        self.tail = max(Parameters.TAIL_LOW, min(Parameters.TAIL_HIGH, self.tail))

        self.left_eye.set_state(self.left_eye.eye_with_position((1, 1)))
        self.right_eye.set_state(self.right_eye.eye_with_position((2, 1)))

    def wag_tail(self, offset=45, speed=6):
        # change tail speed by 'speed' in given direction
        self.tail += speed * self._wag_direction

        # Reverse at bounds
        if self.tail >= Parameters.TAIL_MID + offset:
            self.tail = Parameters.TAIL_MID + offset
            self._wag_direction = -1
        elif self.tail <= Parameters.TAIL_MID - offset:
            self.tail = Parameters.TAIL_MID - offset
            self._wag_direction = 1

    def mad(self, offset=15):
        """
        Straight tail, closed eye, wiggle ears
        """
        self.tail = Parameters.TAIL_MID
        self.left_eye.set_state(self.left_eye.angry_left)
        self.right_eye.set_state(self.right_eye.angry_right)

        self.ear += 4 * self._ear_direction
        if self.ear >= Parameters.EAR_DEFAULT + offset:
            self.ear = Parameters.EAR_DEFAULT + offset
            self._wag_direction = -1
        elif self.ear <= Parameters.EAR_DEFAULT - offset:
            self.ear = Parameters.EAR_DEFAULT - offset
            self._wag_direction = 1

    def blink(self, elapsed):
        """
        Blink eyes, move ears
        """
        # Time within the blink cycle
        t = elapsed % 2  # 2 seconds between blinks

        if t < 0.5:  # seconds eyes stay closed
            # Eyes closed
            self.left_eye.set_state(self.left_eye.blink)
            self.right_eye.set_state(self.right_eye.blink)
        else:
            # Eyes open
            self.left_eye.set_state(self.left_eye.eye_with_position((1, 1)))
            self.right_eye.set_state(self.right_eye.eye_with_position((2, 1)))

        if elapsed < 2:
            self.ear = max(Parameters.EAR_LOW, self.ear - 1)

        elif elapsed < 5:
            self.ear = min(Parameters.EAR_HIGH, self.ear + 1)

    def sleep(self):
        """
        Sleep behavior:
        - Ears fold inside
        - Tail curl to the right
        - Eyes show the "sleeping" pattern
        """
        self.left_speed = 0
        self.right_speed = 0
        self.ear = max(Parameters.EAR_LOW, self.ear - 2)
        self.tail = min(Parameters.TAIL_HIGH, self.tail + 3)
        self.left_eye.set_state(self.left_eye.sleeping)
        self.right_eye.set_state(self.right_eye.sleeping)

    def chase_tail(self, elapsed):
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
        if not hasattr(self, "_frame_index"):
            self.tail = Parameters.TAIL_LOW
            self._frame_index = 0
            self._last_frame_time = 6

        # Phase 0: Tail wags
        if elapsed < 0.5:
            # move fast to one side
            if self.tail <= Parameters.TAIL_HIGH:
                self.tail += 8

        # Phase 1: Look at tail
        elif elapsed < 1:  # look for 1 - 0.5 = 0.5 seconds
            self.left_eye.set_state(self.left_eye.eye_with_position((3, 2)))
            self.right_eye.set_state(self.right_eye.eye_with_position((3, 2)))

        # Phase 2: Spin and counter-tail movement
        elif elapsed < 2:  # starts chasing its tail
            self.left_speed = -Parameters.SPEED_HIGH
            self.right_speed = Parameters.SPEED_HIGH

        elif elapsed < 6:
            self.left_speed = Parameters.SPEED_HIGH
            self.right_speed = -Parameters.SPEED_HIGH
            # tail starts to move in opposite direction, stops when angle=60
            self.tail = max(30, self.tail - 2)

        # Phase 3: Dizzy animation
        elif elapsed < 9:
            self.left_speed = 0
            self.right_speed = 0          
            # Change frames every 0.1s
            if elapsed - self._last_frame_time > 0.1:
                self._last_frame_time += 0.1
                self._frame_index = (self._frame_index + 1) % len(
                    self._left_rotate_frames
                )
                print(self._frame_index)
                print(self._last_frame_time)
            self.left_eye.current_state = self._left_rotate_frames[self._frame_index]
            self.right_eye.current_state = self._right_rotate_frames[self._frame_index]

        # Phase 4: Blink twice
        elif elapsed < 10:
            if int(str(elapsed)[2]) == 2 or int(str(elapsed)[2]) == 6:
                self.left_eye.set_state(self.left_eye.blink)
                self.right_eye.set_state(self.right_eye.blink)
            else:
                self.left_eye.set_state(self.left_eye.eye_with_position((1, 1)))
                self.right_eye.set_state(self.right_eye.eye_with_position((2, 1)))

        # Phase 4: End behavior
        else:
            del self._frame_index
            del self._last_frame_time

        return None

    def wiggle(self, elapsed):
        """
        Changes left and right motor speeds to wiggle

        Args:
            elapsed (number): Time since outer behavior started, in seconds

        Returns:
            None
        """

        if math.floor(elapsed) % 2 == 0:  # even number of seconds elapsed
            self.left_speed = Parameters.SPEED_HIGH
            self.right_speed = Parameters.SPEED_LOW
        else:
            self.left_speed = Parameters.SPEED_LOW
            self.right_speed = Parameters.SPEED_HIGH

    def look_around(self, elapsed):
        """
        Look left and look right, then turn back, and wiggle forward a bit
        """
        if elapsed < 1.5:
            self.left_speed = -Parameters.SPEED_LOW
            self.right_speed = Parameters.SPEED_LOW
            self.left_eye.set_state(self.left_eye.eye_with_position((0, 2)))
            self.right_eye.set_state(self.right_eye.eye_with_position((0, 2)))

        elif elapsed < 4:
            self.left_speed = Parameters.SPEED_LOW
            self.right_speed = -Parameters.SPEED_LOW
            self.left_eye.set_state(self.left_eye.eye_with_position((3, 2)))
            self.right_eye.set_state(self.right_eye.eye_with_position((3, 2)))

        elif elapsed < 5:
            self.left_speed = -Parameters.SPEED_LOW
            self.right_speed = Parameters.SPEED_LOW

        elif elapsed < 7:
            self.wiggle(elapsed)

        elif elapsed < 9:
            self.left_eye.set_state(self.left_eye.squint_left)
            self.right_eye.set_state(self.right_eye.squint_right)

    def petted(self, state):
        """
        Triggered when button on top is pressed
        Stops any movement, smiling/squint eyes, wag tail, fold ears
        """
        self.left_speed = 0
        self.right_speed = 0
        if state == "happy":
            self.left_eye.set_state(self.left_eye.happy)
            self.right_eye.set_state(self.right_eye.happy)
        elif state == "squint":
            self.left_eye.set_state(self.left_eye.squint_left)
            self.right_eye.set_state(self.right_eye.squint_right)

        self.wag_tail(speed=2)
        self.ear = Parameters.EAR_LOW

    def look_for_treat(self, elapsed):
        """
        React to melody
        Spins and look around for treat, comes to the treat
        When sees treat, make heart eyes, wag tail, comes to the treat
        """
        LEFT_THRESHOLD = 200
        RIGHT_THRESHOLD = 280

        berry_position = self.berry_detection.get_berry_position()
        # print(berry_position)

        if elapsed > 20:
            self.mad()
            self.left_speed = 0
            self.right_speed = 0
            return

        self.left_eye.set_state(self.left_eye.heart_left)
        self.right_eye.set_state(self.right_eye.heart_right)
        self.wag_tail()

        if berry_position is None:
            self.left_speed = -Parameters.SPEED_HIGH
            self.right_speed = Parameters.SPEED_HIGH

        else:
            x_position = berry_position[0]
            if x_position > RIGHT_THRESHOLD:  # berry is to the right
                self.left_speed = Parameters.SPEED_LOW
                self.right_speed = -Parameters.SPEED_LOW
            elif x_position > LEFT_THRESHOLD:  # berry is in the middle
                self.left_speed = Parameters.SPEED_HIGH
                self.right_speed = Parameters.SPEED_HIGH
            else:  # berry is to the left
                self.left_speed = -Parameters.SPEED_LOW
                self.right_speed = Parameters.SPEED_LOW
