import speech_recognition
import pyttsx3
import time
from queue import Queue


class WordDetection:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.commands = ['spin', 'square', 'circle']
        self.queue = Queue()
        self.mic = speech_recognition.Microphone()

        with self.mic as mic:
            self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)

        # Start background listener
        self.stop_fn = self.recognizer.listen_in_background(
            self.mic, self._callback
        )

    def _callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio).lower()
            print("Heard:", text)

            for cmd in self.commands:
                if cmd in text:
                    self.queue.put(cmd)  # store command
                    break

        except speech_recognition.UnknownValueError:
            pass

    def read_cmd(self):
        if not self.queue.empty():
            return self.queue.get()  # return earliest command
        
        return None  # no command this cycle
    
# detector=WordDetection()

# while True:
#     cmd = detector.read_cmd()
#     print(cmd)
#     if cmd == 'spin':
#         print('set run_spin to high')
#     time.sleep(0.02)



# def update_word_command(self, now):
#     new_command = self.word_detector.read_cmd()

#     if new_command is not None:
#         self.command = new_command
#         self.word_command_start = now

#     if self.command is not None and now - self.word_command_start <= 10:
#         self.run_signals["run_spin"] = 1 if self.command == "spin" else 0
#         self.run_signals["run_circle"] = 1 if self.command == "circle" else 0
#         self.run_signals["run_square"] = 1 if self.command == "square" else 0

#     else:
#         self.run_signals["run_spin"] = 0
#         self.run_signals["run_circle"] = 0
#         self.run_signals["run_square"] = 0
#         self.command = None
