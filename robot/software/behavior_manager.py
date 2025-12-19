import time
import random
from robot.software.berry_detection import BerryDetection
from robot.software.audio_processing import CollectAudio


class StateManager:

    def __init__(self, arduino):
        """
        Manages robot states and behavior signals based on input signals
        Handles prioritization of behaviors and idle behavior loop.
        """
        self.berry_detection = BerryDetection()
        self.audio_collector = CollectAudio()
        self.arduino = arduino

        # Run signals: 1 = active, 0 = inactive
        # Priority is order in dict (earlier = higher priority)
        self.run_signals = {
            "run_petted": 0,
            "run_look_for_treat": 0,
            "run_sleep": 0,
        }

        # Idle behaviors and durations
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

        # Input / behavior tracking
        self.button_pressed = False
        self.heard_melody = False
        self.dark = False

        # Timing tracking
        self.now = None
        self.default_start = None
        self.idle_start = None
        self.petted_start = None
        self.look_for_treat_start = None
        self.sleep_start = None

        self.eye_state = "happy"  # default eye state when petted
        self.chase_tail_phase = 0

    def update_petted(self, now):
        """Check button press and update petted behavior."""
        line = self.arduino.read(1)  # Read 1 byte
        if line:
            # Decode byte to string and strip whitespace
            self.button_pressed = line.decode()

        if self.button_pressed == "1":
            self.petted_start = now
            self.run_signals["run_look_for_treat"] = 0
            self.look_for_treat_start = None

        if (
            self.petted_start is not None and now - self.petted_start <= 3
        ):  # reaction lasts for 3 sec
            self.run_signals["run_petted"] = 1
        else:
            self.run_signals["run_petted"] = 0
            self.eye_state = random.choice(["happy", "squint"])

    def update_melody(self, now):
        """Check for melody detection and update look for treat behavior."""
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

    def update_sleep(self, now):
        """Check darkness and update sleep behavior."""
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
        """
        Update all run signals and set current active behavior.
        Their order in the list matters of more than 1 happens the same time.
        """
        self.update_petted(now)
        self.update_melody(now)
        # self.update_word_command(now)
        self.update_sleep(now)

        self.run_signal = 0
        for state, signal in self.run_signals.items():
            if signal == 1:
                self.run_signal = 1
                self.state = state
                break  # once find an active signal, stop enumerating

    def update_state(self):
        """
        Main state update loop:
        - Updates current time and signals
        - Chooses active behavior or idle/default loop
        """
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
