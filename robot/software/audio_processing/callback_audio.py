import pyaudio
import time
import wave

import pitch_finder as pf

WIDTH = 2
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

frames = []


def callback(in_data, frame_count, time_info, status):
    global frames
    frames.append(in_data)

    return in_data, pyaudio.paContinue


stream = p.open(
    format=p.get_format_from_width(WIDTH),
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    stream_callback=callback,
)

stream.start_stream()

last_sample = time.time()

while stream.is_active():
    if time.time() - last_sample >= 2:
        with wave.open(
            "output.wav", "wb"
        ) as wf:  # TODO: put this in the correct directory
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))

        y, sr = pf.load_audio("output.wav")
        f0 = pf.estimate_pitch(y, sr)
        print("f0:", f0)
        if len(f0) != 0:
            notes = pf.pitch_to_note(f0)
            print("notes:", notes)

        last_sample = time.time()
        frames = []

    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()


"""

declare callback function
open and start stream

initialize series of notes

in main loop:
    every .02 seconds (or whatever), check to see if 1 second has passed
    if 1 second has passed:
        save it to a file and run audio processing to get notes
        add new notes to series of notes
        check for melody

"""
