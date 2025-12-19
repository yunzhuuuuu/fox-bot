import time
import wave
import os
import pyaudio
import numpy as np
import sounddevice
import librosa


def load_audio(filename: str):
    """Return waveform (y) and sampling rate (sr) from a file in the current directory."""
    MEDIA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "media")
    audio_path = os.path.join(MEDIA_DIR, filename)
    y, sr = librosa.load(audio_path)
    # print(sr)
    print("loading and analyzing audio")
    return y, sr


def estimate_pitch(y, sr, fmin_note="C3", fmax_note="C7"):
    """
    Estimate fundamental frequency (f0) using probabilistic YIN.
    Return an array of all recognized frequences.
    """
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz(fmin_note), fmax=librosa.note_to_hz(fmax_note)
    )
    return f0[voiced_flag]


def pitch_to_note(f0, min_instances=5):
    """
    Convert an array of fundamental frequencies (f0) to musical note names,
    keeping only notes that appear consecutively at least a certain amount of times.
    """
    notes = librosa.hz_to_note(f0)
    cleaned_notes = []
    count = 1

    for i in range(1, len(notes)):
        if notes[i] == notes[i - 1]:
            count += 1
        else:
            if count >= min_instances:
                cleaned_notes.append(str(notes[i - 1]))
            count = 1
    # Handle last sequence
    if count >= min_instances:
        cleaned_notes.append(str(notes[-1]))

    return cleaned_notes


class CollectAudio:

    WIDTH = 2
    CHANNELS = 1
    RATE = 44100

    MELODY = np.array(["A4", "A♯4", "G4", "A4", "D4", "A4", "F4", "C5"])

    def __init__(self):
        self.num_correct_notes = 0

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

    def detect_melody(self, save_interval=2, max_incorrect_notes=-1):
        """
        Save audio if more than 2 seconds has passed since the last save, and detect notes

        Args:
            save_interval (Int) (optional): Number of seconds between each save (defaults to 2)
            max_incorrect_notes (Int) (optional): Maximum number of incorrect notes that can be
                between correct notes. If -1, then there is no limit to incorrect notes. Defaults
                to -1

        Returns:
            Boolean: Whether or not the notes match the set melody
        """
        is_melody = False
        if time.time() - self.last_sample >= save_interval:

            media_dir = os.path.join(os.path.dirname(__file__), "..", "..", "media")
            audio_path = os.path.join(media_dir, "output.wav")
            with wave.open(audio_path, "wb") as wf:
                wf.setnchannels(CollectAudio.CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(CollectAudio.RATE)
                wf.writeframes(b"".join(self.frames))

            y, sr = load_audio("output.wav")
            f0 = estimate_pitch(y, sr)
            if len(f0) != 0:  # if there are detected pitches
                notes = pitch_to_note(f0, min_instances=2)
                print(notes)

                while True:
                    next_note: str = CollectAudio.MELODY[self.num_correct_notes]
                    try:
                        index_of_note: int = notes.index(next_note)
                    except ValueError:  # next correct note was not found
                        break

                    # note exists and there's not that many incorrect notes, or ignore incorrect notes if -1
                    if (
                        index_of_note <= max_incorrect_notes
                        or max_incorrect_notes == -1
                    ):
                        self.num_correct_notes += 1  # increment correct notes
                        notes = notes[
                            index_of_note + 1 :
                        ]  # cut off already used part of notes array
                        if self.num_correct_notes == len(
                            CollectAudio.MELODY
                        ):  # if entire melody is there
                            self.num_correct_notes = 0  # reset correct notes
                            is_melody = True
                            break

            self.last_sample = time.time()
            self.frames = []

        return is_melody
