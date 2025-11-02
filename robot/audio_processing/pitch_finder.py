# Pitch finder example
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt

# frequencies = {
#     "C4": 261,
#     "C#4": 277,
#     "D": 293,
#     "D#": 311,
#     "E": 329,
#     "F": 349,
#     "F#": 369,
#     "G": 392,
#     "G#": 415,
#     "A": 440,
#     "A#": 466,
#     "B": 492,
# }

def load_audio(filename: str):
    """Return waveform (y) and sampling rate (sr) from a file in the current directory."""
    path = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(path, filename)
    y, sr = librosa.load(audio_path)
    print(sr)
    print("loading audio and yin-ing")
    return y, sr


def estimate_pitch(y, sr, fmin_note="C3", fmax_note="C7"):
    """
    Estimate fundamental frequency (f0) using probabilistic YIN.
    Return an array of all recognized frequences.
    """
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz(fmin_note),
        fmax=librosa.note_to_hz(fmax_note)
    )
    return f0[voiced_flag]


def pitch_to_note(f0, min_instances=5):
    """
    Convert an array of fundamental frequencies (f0) to musical note names,
    keeping only notes that appear consecutively at least a certain amount of times.
    """
    notes = librosa.hz_to_note(f0)
    print(notes)
    cleaned_notes = []
    count = 1

    for i in range(1, len(notes)):
        if notes[i] == notes[i - 1]:
            count += 1
        else:
            if count >= min_instances:
                cleaned_notes.append(notes[i - 1])
            count = 1
    # Handle last sequence
    if count >= min_instances:
        cleaned_notes.append(notes[-1])

    return np.array(cleaned_notes)    

if __name__ == "__main__":
    y, sr = load_audio("media/output_audio.wav")
    f0 = estimate_pitch(y, sr)
    notes = pitch_to_note(f0, 8)
    # print(f0)
    print(notes)

# fig, ax = plt.subplots()  # Create a figure containing a single Axes.
# ax.plot(f0)  # Plot some data on the Axes.

# plt.axhline(261)
# plt.axhline(277)
# plt.axhline(293)
# plt.axhline(311)
# plt.axhline(329)
# plt.axhline(349)
# plt.axhline(369)
# plt.axhline(392)
# plt.axhline(415)
# plt.axhline(440)
# plt.axhline(466)
# plt.axhline(493)
# plt.axhline(523)
# plt.axhline(554)

# plt.show()
