# Pitch finder example
import librosa
import numpy as np

# Load the audio as a waveform `y`
# Store the sampling rate as `sr`
y, sr = librosa.load(librosa.example('trumpet'))

# Estimate fundamental frequency (f0) with probabilistic YIN
f0, voiced_flag, voiced_probs = librosa.pyin(
    y,
    fmin=librosa.note_to_hz('C2'),
    fmax=librosa.note_to_hz('C7')
)

# Replace unvoiced frames with NaN
f0 = np.where(voiced_flag, f0, np.nan)

print(f0)
# notes = librosa.hz_to_note(f0)
# print(notes)
