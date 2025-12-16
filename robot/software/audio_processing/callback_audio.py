import time
import wave
import os
import pyaudio
import robot.software.audio_processing.pitch_finder as pf
import numpy as np
import sounddevice


class CollectAudio:

    WIDTH = 2
    CHANNELS = 1
    RATE = 44100

    MELODY = np.array(["A4", "A♯4", "G4", "A4", "D4", "A4", "F4", "C5"])

    def __init__(self):
        self.saved_notes = []

        self.p = pyaudio.PyAudio()
        self.frames = []

        def callback(in_data, frame_count, time_info, status):
            """
            Callback function to be called for audio data
            """
            self.frames.append(in_data)
            return in_data, pyaudio.paContinue

        self.stream = self.p.open(
            format=self.p.get_format_from_width(CollectAudio.WIDTH),
            channels=CollectAudio.CHANNELS,
            rate=CollectAudio.RATE,
            input=True,
            output=False,
            stream_callback=callback,
        )

        self.last_sample = time.time()
        self.stream.start_stream()

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()

    def detect_melody(self, save_interval=2):
        """
        Save audio if more than 2 seconds has passed since the last save, and detect notes

        Args:
            save_interval (Int) (optional): Number of seconds between each save

        Returns:
            Boolean: Whether or not the notes match the set melody
        """
        if time.time() - self.last_sample >= save_interval:

            is_melody = False

            media_dir = os.path.join(os.path.dirname(__file__), "..", "..", "media")
            audio_path = os.path.join(media_dir, "output.wav")
            with wave.open(audio_path, "wb") as wf:
                wf.setnchannels(CollectAudio.CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(CollectAudio.RATE)
                wf.writeframes(b"".join(self.frames))

            y, sr = pf.load_audio("output.wav")
            f0 = pf.estimate_pitch(y, sr)
            if len(f0) != 0:
                notes = pf.pitch_to_note(f0, min_instances=3)
                # remove duplicate if last note of saved and 1st note of new list are the same
                if (
                    len(self.saved_notes) != 0
                    and len(notes) != 0
                    and self.saved_notes[-1] == notes[0]
                ):
                    notes = notes[1:]

                self.saved_notes.extend(notes)
                print(str(self.saved_notes).encode("utf-8"))
                # print(str(notes).encode("utf-8"))

                is_melody = pf.check_melody(self.saved_notes, CollectAudio.MELODY)
                print(is_melody)
                if is_melody:
                    self.saved_notes = []

            self.last_sample = time.time()
            self.frames = []

            return is_melody
