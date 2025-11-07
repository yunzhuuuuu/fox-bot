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


def check_melody(notes, melody):
    for i in range(len(notes) - len(melody) + 1):
        if np.array_equal(notes[i : i + len(melody)], melody):
            return True
    return False


def run_pitch_finder(audio_path, min_instances=5):
    """
    High-level wrapper that loads audio, detects pitch, and checks melody.
    Returns True if certain melody is found, otherwise false
    """
    melody = np.array(["A3", "A♯3", "G3", "A3", "D3", "A3", "F3", "C4"])
    y, sr = load_audio(audio_path)
    f0 = estimate_pitch(y, sr)
    # print(f0)
    notes = pitch_to_note(f0, min_instances)
    print(notes)
    is_melody = check_melody(notes, melody)
    print(is_melody)
    return is_melody


if __name__ == "__main__":
    run_pitch_finder("media/output_audio.wav", 8)


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
