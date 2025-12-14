import time
import random
import struct
import math
import robot.software.eye_display as eye_display
from robot.software.berry_detection import BerryDetection
from robot.software.behaviors import RobotBehaviors
from robot.software.audio_processing.word_detection import WordDetection

class StateManager:

    def __init__(self, button_pressed, seen_treat, heard_melody):
        self.berry_detection = BerryDetection()
        self.behaviors = RobotBehaviors()
        self.word_detector = WordDetection()

        self.button_pressed = button_pressed
        self.seen_treat = seen_treat
        self.heard_melody = heard_melody

        # if run_signal is 1, the robot should be doing this behavior, if 0, it should not
        # ideally only one of them should be 1, but if there's more than 1 active signals, 
        # the signals closer to the beginning of the dict has higher priority to happen
        # higher priority behavior interrupts lower priority ones
        self.run_signals = {
            "run_petted": 0, 
            "run_look_for_treat": 0, 
            "run_spin": 0, 
            "run_circle": 0, 
            "run_square": 0
            }
        
        self.idles = ["sleep", "chase_tail", "wag_tail"]
        self.idle_duration = {"sleep": 5, "chase_tail": 4, "wag_tail": 3}

        self.run_signal = 0
        self.state = "default"
        self.behavior = self.behaviors.default

        self.command = None
        self.default_start = None
        self.idle_start = None
        self.petted_start = None
        self.look_for_treat_start = None
        self.chase_tail_phase = 0

    def update_petted(self, now):
        if self.button_pressed:
            self.petted_start = time.time()

        if self.petted_start is not None and now - self.petted_start <= 5: # reaction lasts for 5 sec
            self.run_signals["run_petted"] = 1
        else:
            self.run_signals["run_petted"] = 0

    def update_melody(self, now):
        if self.heard_melody:
            self.look_for_treat_start = time.time()

        if self.look_for_treat_start is not None and now - self.look_for_treat_start <= 20: # look for treat for at most 20 sec
            self.run_signals["run_look_for_treat"] = 1
        else:
            self.run_signals["run_look_for_treat"] = 0

    def update_word_command(self):
        self.command = self.word_detector.read_cmd()
        
        if self.command is not None:
            # heard some command
            self.run_signals["run_spin"] = 0
            self.run_signals["run_circle"] = 0
            self.run_signals["run_square"] = 0 

            if self.command == "spin":
                self.run_signals["run_spin"] = 1

            elif self.command == "circle":
                self.run_signals["run_circle"] = 1
            
            elif self.command == "square":
                self.run_signals["run_square"] = 1

        # TODO: set to 0 when done
        # if self.spin_done:

    # TODO: chase tail phase update

    def update_signal(self, now):
        self.update_petted(now)
        self.update_melody(now)
        self.update_word_command()

        self.run_signal = 0
        for state, signal in self.run_signals.items():
            if signal == 1:
                self.run_signal = 1
                self.state = state
                break # once find an active signal, stop enumerating

    def update_state(self, now):
        # update incoming signals and run corresponding active behavior
        self.update_signal(now)

        # if there's no active behavior running, run idle-default loop
        if self.run_signal == 0:
            # was in default
            if self.state == "default":
                if self.default_start is None:
                    self.default_start = now

                if now - self.default_start >= 5:
                    self.state = random.choice(self.idles)
                    self.idle_start = now

            # was running idle
            elif self.state in self.idles:
                duration = self.idle_duration[self.state]
                if now - self.idle_start >= duration:
                    self.state = "default"
                    self.default_start = None
                    self.idle_start = None

            # was running an active behavior but just ended
            else:
                self.state = "default"
                self.default_start = now

    def update(self):
        now = time.time()
        self.update_state(now)

        match self.state:
            case "run_petted":
                self.behavior = self.behaviors.petted
            case "run_look_for_treat":
                self.behavior = self.behaviors.look_for_treat
            case "run_spin":
                self.behavior = self.behaviors.spin
            case "run_circle":
                self.behavior = self.behaviors.circle
            case "run_square":
                self.behavior = self.behaviors.square
            case "sleep":
                self.behavior = self.behaviors.sleep
            case "chase_tail":
                self.behavior = self.behaviors.chase_tail
            case "wag_tail":
                self.behavior = self.behaviors.wag_tail
            case _:
                self.behavior = self.behaviors.default
