# combines all robot components behavior for the idle state

# return array:
# Serial Data format: (21 byte packet)
# Byte 0&1 = Speed to set left&right motors to (-127)-(128)(byte)
# Byte 2 = Servo angle for ears 0-180(byte), mirrored.
#    face forward: 90, inside: decrease, outside: increase
# Byte 3 = Servo angle for the tail 0-180(byte)
# Byte 4 = Brightness of the eyes (0-1)
# Bytes 5-12 = Array for the left eye
# Bytes 13-20 = Array for the right eye


import time
import random
import struct
import math

# from enum import Enum
import robot.software.eye_display as eye_display


# class SpinDirection(Enum):
#     STOP = 0
#     LEFT = 1
#     RIGHT = 2


class RobotBehaviors:

    def __init__(self, button_pressed, seen_treat):
        # WHEEL_CIRCUMFERENCE = 8.482  # inches
        # BETWEEN_WHEELS = 6  # inches TODO: get actual measurement

        # initialize robot components
        self.left_speed = 0  # 0–255
        self.right_speed = 0  # 0–255
        # self.spin = 180  # 0–360
        self.ear = 90  # 0–180
        self.tail = 120  # 0–180
        self.eye_brightness = 1  # for formatting
        self.left_eye = eye_display.EyeDisplay()
        self.right_eye = eye_display.EyeDisplay()
        # self.eye = [0] * 64  # eye array (8 bytes)

        self.last_behavior_end = time.time()
        self.in_idle_behavior = False
        self.behavior = None

        # self.current_angle = 0  # 0 to 360
        # self.l_encoder_prev = 0
        # self.r_encoder_prev = 0

        self.l_encoder_updated = 0  # TODO: update encoder values every loop
        self.r_encoder_updated = 0

        # self.spin_dir = SpinDirection.STOP
        # self.target_angle = 0  # 0 to 360

        self.chase_tail_phase = 0

        self.button_pressed = button_pressed
        self.seen_treat = seen_treat

    def default(self):
        """
        Passive idle, called when not running a special behavior.

        Slowly reduces movement until static, ears face forward, neutral tail,
        and sets eyes to a centered gaze.
        """
        self.left_speed = max(0, self.left_speed - 2)
        self.right_speed = max(0, self.right_speed - 2)
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
        self.left_eye.set_state(self.left_eye.eye_with_position((1, 1)))
        self.right_eye.set_state(self.right_eye.eye_with_position((2, 1)))

    def build_packet(self):
        """
        Returns 21-byte format Arduino expects:
        <bb B B B 8s 8s>
        L  R  ear tail bright  leftEye  rightEye
        """
        # pack:
        # [0]   left motor  (-127-128)
        # [1]   right motor (-127-128)
        # [2]   ear servo   (0-180)
        # [3]   tail servo  (0-180)
        # [4]   eye brightness (0-1 → scaled to 0–255)
        # [5-12]   left eye  8 bytes
        # [13-20]  right eye 8 bytes
        return struct.pack(
            "<bbBBB8B8B",
            int(self.left_speed),
            int(self.right_speed),
            int(self.ear),
            int(self.tail),
            self.eye_brightness,
            *self.left_eye.current_state,
            *self.right_eye.current_state
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

        self.left_speed = 0
        self.right_speed = 0
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
        self.left_eye.set_state(self.left_eye.sleeping)
        self.right_eye.set_state(self.right_eye.sleeping)

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

            # print(self._rotate_frames)
            self._frame_index = 0
            self._last_frame_time = None

        self._left_rotate_frames = self.left_eye.eye_rotate(1)  # clockwise
        self._right_rotate_frames = self.right_eye.eye_rotate(0)  # counterclock
        now = time.time()
        elapsed = now - self._behavior_start

        # Phase 0: Tail wags
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
            self.left_eye.set_state(self.left_eye.eye_with_position((3, 2)))
            self.right_eye.set_state(self.right_eye.eye_with_position((3, 2)))
            if elapsed > 0.8:  # look for 0.8 - 0.5 = 0.3 seconds
                self.chase_tail_phase = 2

        # Phase 2: Spin and counter-tail movement
        elif self.chase_tail_phase == 2:
            if elapsed < 3:  # chases its tail for about 3 - 0.5 - 0.3 = 2.2 seconds
                # self.spin = min(360, self.spin + 2)
                self.left_speed = 60
                self.right_speed = -60
            if elapsed > 1:
                # tail starts to move in opposite direction after 1 second, stops when angle=75
                self.tail = max(75, self.tail - 2)

            if elapsed > 3:
                self.chase_tail_phase = 3
                self._frame_index = 0
                self._last_frame_time = now

        # Phase 3: Dizzy animation
        elif self.chase_tail_phase == 3:
            # Change frames every 0.1s
            if now - self._last_frame_time > 0.1:
                self._last_frame_time = now
                self._frame_index += 1

                if self._frame_index >= len(self._left_rotate_frames):
                    self.chase_tail_phase = 4
                else:
                    self.left_eye.current_state = self._left_rotate_frames[
                        self._frame_index
                    ]
                    self.right_eye.current_state = self._right_rotate_frames[
                        self._frame_index
                    ]
                    print(self.left_eye.current_state)

        # Phase 4: End behavior
        if self.chase_tail_phase == 4:
            self.in_idle_behavior = False
            self.last_behavior_end = time.time()
            del self._behavior_start
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
            self.left_speed = 60
            self.right_speed = -50
        else:
            self.left_speed = 50
            self.right_speed = -60

    def petted(self):
        """
        Triggered when button on top is pressed
        Stops any movement, smiling eyes, wag tail, move ears
        """
        pass

    def wander(self):
        """
        Wiggle and move in a certain pattern tbd
        """
        pass

    def hear_melody(self):
        """
        Spins and look around for treat, comes to the treat
        """
        pass

    def see_treat(self):
        """
        Heart eyes, wag tail
        """
        self.left_eye.set_state(self.left_eye.heart_left)
        self.right_eye.set_state(self.right_eye.heart_right)

        if not hasattr(self, "_wag_direction"):
            self._wag_direction = 1  # 1 = increasing, -1 = decreasing

        # change tail speed by '2' in given direction
        self.tail += 2 * self._wag_direction

        # Reverse at bounds
        if self.tail >= 135:
            self.tail = 135
            self._wag_direction = -1
        elif self.tail <= 45:
            self.tail = 45
            self._wag_direction = 1

    # more states

    def update(self):
        """
        Called every time frame. Handles:
        - Starting idle behavior every 10 sec
        - Running idle behavior for 5 sec
        - Returning to default() after that
        """

        now = time.time()

        # priority 1: petted
        if self.button_pressed:
            self.petted()
            return

        # priority 2: hear melody

        # priority 3: see treat
        if self.seen_treat:
            self.see_treat()
            return

        # priority 4: idles
        if self.in_idle_behavior:
            self.behavior()
            return

        # Default state until it's time to start an idle
        if now - self.last_behavior_end >= 5.0:
            # # update angle
            # delta_l = (
            #     RobotBehaviors.WHEEL_CIRCUMFERENCE
            #     * (self.l_encoder_updated - self.l_encoder_prev)
            #     / 360
            # )  # L wheel movement in inches
            # delta_r = (
            #     RobotBehaviors.WHEEL_CIRCUMFERENCE
            #     * (self.r_encoder_updated - self.r_encoder_prev)
            #     / 360
            # )  # R wheel movement in inches
            # delta_theta = (
            #     delta_l - delta_r
            # ) / RobotBehaviors.BETWEEN_WHEELS  # change in robot angle, in radians
            # self.current_angle += math.degrees(delta_theta)  # add to current robot angle

            # self.l_encoder_prev = self.l_encoder_updated
            # self.r_encoder_prev = self.r_encoder_updated
            self.in_idle_behavior = True
            behaviors = [
                self.sleep,
                self.chase_tail,
            ]  # add self.chase_tail and others when ready
            self.behavior = random.choice(behaviors)
        # elif self.spin_dir != SpinDirection.STOP:
        #     if (  # spinning left and reached desired angle
        #         self.spin_dir == SpinDirection.LEFT
        #         and self.current_angle > self.target_angle
        #     ) or (  # spinning right and reached desired angle
        #         self.spin_dir == SpinDirection.RIGHT
        #         and self.current_angle < self.target_angle
        #     ):
        #         self.spin_dir = SpinDirection.STOP
        #         self.target_angle = 0
        else:
            # Normal default state
            self.default()


if __name__ == "__main__":
    button_pressed = 0
    seen_treat = 0
    fox = RobotBehaviors(button_pressed, seen_treat)
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
        print(fox.left_eye.current_state)
        print(fox.right_eye.current_state)
