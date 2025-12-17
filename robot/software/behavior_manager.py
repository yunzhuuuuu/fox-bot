import time
import random

from robot.software.berry_detection import BerryDetection

# from robot.software.audio_processing.word_detection import WordDetection
from robot.software.audio_processing.callback_audio import CollectAudio


class StateManager:

    def __init__(self, arduino):
        self.berry_detection = BerryDetection()
        # self.word_detector = WordDetection()
        self.audio_collector = CollectAudio()
        self.arduino = arduino

        # if run_signal is 1, the robot should be doing this behavior, if 0, it should not
        # ideally only one of them should be 1, but if there's more than 1 active signals,
        # the signals closer to the beginning of the dict has higher priority to happen
        # higher priority behavior interrupts lower priority ones
        self.run_signals = {
            "run_petted": 0,
            "run_look_for_treat": 0,
            # "run_spin": 0,
            # "run_circle": 0,
            # "run_square": 0,
            "run_sleep": 0,
        }

        self.idles = ["chase_tail", "wag_tail", "blink", "look_around"]
        self.idle_duration = {
            "chase_tail": 10,
            "wag_tail": 3,
            "blink": 6,
            "look_around": 12,
        }
        # active behavior durations are in their run signal logics

        self.run_signal = 0
        self.state = "default"

        self.button_pressed = False
        self.heard_melody = False
        self.dark = False
        self.command = None
        self.now = None
        self.default_start = None
        self.idle_start = None
        self.petted_start = None
        self.eye_state = "happy"  # default eye state when petted
        self.look_for_treat_start = None
        self.word_command_start = None
        self.sleep_start = None
        self.chase_tail_phase = 0

    def update_petted(self, now):
        line = self.arduino.read(1)  # Read 1 byte
        if line:
            # Decode byte to string and strip whitespace
            self.button_pressed = line.decode()

        if self.button_pressed == "1":
            self.petted_start = now

        if (
            self.petted_start is not None and now - self.petted_start <= 3
        ):  # reaction lasts for 3 sec
            self.run_signals["run_petted"] = 1
        else:
            self.run_signals["run_petted"] = 0
            self.eye_state = random.choice(["happy", "heart", "sparkle"])

    def update_melody(self, now):
        self.heard_melody = self.audio_collector.detect_melody()
        if self.heard_melody:
            self.look_for_treat_start = now

        if (
            self.look_for_treat_start is not None
            and now - self.look_for_treat_start <= 25
        ):  # look for treat for at most 20 sec
            self.run_signals["run_look_for_treat"] = 1
        else:
            self.run_signals["run_look_for_treat"] = 0

    def update_word_command(self, now):
        # new_command = self.word_detector.read_cmd()
        new_command = None

        if new_command is not None:
            self.command = new_command
            self.word_command_start = now

        if self.command is not None and now - self.word_command_start <= 10:
            self.run_signals["run_spin"] = 1 if self.command == "spin" else 0
            self.run_signals["run_circle"] = 1 if self.command == "circle" else 0
            self.run_signals["run_square"] = 1 if self.command == "square" else 0

        else:
            self.run_signals["run_spin"] = 0
            self.run_signals["run_circle"] = 0
            self.run_signals["run_square"] = 0
            self.command = None

    def update_sleep(self, now):
        self.dark = self.berry_detection.get_darkness()
        # 1 if dark environment, 0 if not
        if self.dark:
            self.sleep_start = now

        if (
            self.sleep_start is not None and now - self.sleep_start <= 2
        ):  # 2 second wake up delay
            self.run_signals["run_sleep"] = 1
        else:
            self.run_signals["run_sleep"] = 0

    def update_signal(self, now):
        self.update_petted(now)
        self.update_melody(now)
        self.update_word_command(now)
        self.update_sleep(now)

        self.run_signal = 0
        for state, signal in self.run_signals.items():
            if signal == 1:
                self.run_signal = 1
                self.state = state
                break  # once find an active signal, stop enumerating

    def update_state(self):
        self.now = time.time()
        # update incoming signals and run corresponding active behavior
        self.update_signal(self.now)

        # if there's no active behavior running, run idle-default loop
        if self.run_signal == 0:
            # was in default
            if self.state == "default":
                if self.default_start is None:
                    self.default_start = self.now

                if self.now - self.default_start >= 5:
                    self.state = random.choice(self.idles)
                    self.idle_start = self.now

            # was running idle
            elif self.state in self.idles:
                duration = self.idle_duration[self.state]
                if self.now - self.idle_start >= duration:
                    self.state = "default"
                    self.default_start = None
                    self.idle_start = None

            # was running an active behavior but just ended
            else:
                self.state = "default"
                self.default_start = self.now
