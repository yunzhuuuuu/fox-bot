# Pitch finder example
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt

frequencies = {
    "C4": 261,
    "C#4": 277,
    "D": 293,
    "D#": 311,
    "E": 329,
    "F": 349,
    "F#": 369,
    "G": 392,
    "G#": 415,
    "A": 440,
    "A#": 466,
    "B": 492,
}

path = os.path.dirname(os.path.abspath(__file__))
audio_path = os.path.join(path, "media/beastling_sing.wav")

print("loading")
# Load the audio as a waveform `y`
# Store the sampling rate as `sr`
y, sr = librosa.load(audio_path)

print("pyin")
# Estimate fundamental frequency (f0) with probabilistic YIN
f0, voiced_flag, voiced_probs = librosa.pyin(
    y, fmin=librosa.note_to_hz("C4"), fmax=librosa.note_to_hz("C7")
)

print("replace nan")
# Replace unvoiced frames with NaN
f0 = np.where(voiced_flag, f0, np.nan)

# print(f0)
# notes = librosa.hz_to_note(f0)
# print(notes)

print("remove nan")
f0 = f0[~np.isnan(f0)]

# print("\n")
# print(f0)

fig, ax = plt.subplots()  # Create a figure containing a single Axes.
ax.plot(f0)  # Plot some data on the Axes.

plt.axhline(261)
plt.axhline(277)
plt.axhline(293)
plt.axhline(311)
plt.axhline(329)
plt.axhline(349)
plt.axhline(369)
plt.axhline(392)
plt.axhline(415)
plt.axhline(440)
plt.axhline(466)
plt.axhline(493)
plt.axhline(523)
plt.axhline(554)

plt.show()

# print(librosa.hz_to_note(f0))
