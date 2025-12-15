import os
import librosa
import numpy as np


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


def check_melody(notes, melody):
    """
    Check if given notes match a melody

    Args:
        notes (List<String>): List of note names
        melody (List<String>): List of note names

    Returns:
        Boolean: Boolean representing whether the melody matches
    """
    for i in range(len(notes) - len(melody) + 1):
        if np.array_equal(notes[i : i + len(melody)], melody):
            return True
    return False


def run_pitch_finder(audio_path, min_instances=5):
    """
    High-level wrapper that loads audio, detects pitch, and checks melody.

    Args:
        audio_path (String): Filepath leading to wav file
        min_instances (int): Minimum times a note has to appear to be taken into account in the
            melody. Defaults to 5.

    Returns:
        Boolean: True if certain melody is found, otherwise false
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


# if __name__ == "__main__":
#     run_pitch_finder("output_audio.wav", 8)
