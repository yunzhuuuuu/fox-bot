import wave
import time
import os
import serial
import numpy as np

# Audio Format Settings
SERIAL_PORT = "COM10"  # UPDATE THIS to match actual Arduino's port
BAUD_RATE = 1000000  # Must match SERIAL_BAUD_RATE in Arduino
SERIAL_TIMEOUT = 1  # Seconds

HEADER_BYTE_1 = 0xFF
HEADER_BYTE_2 = 0xFE
# 729 samples * 2 bytes/sample = 1458 bytes
PAYLOAD_SIZE_BYTES = 1458

CHANNELS = 3  # Must match NUM_CHANNELS in Arduino
SAMPLE_RATE = 7500  # Must match SAMPLE_RATE in Arduino
SAMPLE_WIDTH_BYTES = 2  # 16-bit audio (int16_t)

# Path to media folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
MEDIA_DIR = os.path.join(PROJECT_ROOT, "media")
# OUTPUT_FILENAME = os.path.join(MEDIA_DIR, "output_audio.raw")
# OUTPUT_WAV_FILENAME = os.path.join(MEDIA_DIR, "output_audio.wav")

START_TIME = time.time()
all_audio_data = []


def save_audio_wav(data, filename=time.time() - START_TIME):
    """
    Saves audio data (payloads only) to a .wav file.
    """
    print(f"\nSaving audio chunks directly to {filename}...")

    samples = np.frombuffer(
        data, dtype="<i2"
    )  # little-endian('<') 16-bit('i2') signed int

    with wave.open(filename + ".wav", "wb") as f_out:
        f_out.setnchannels(1)
        f_out.setframerate(SAMPLE_RATE)
        f_out.setsampwidth(SAMPLE_WIDTH_BYTES)
        f_out.writeframes(samples.tobytes())

    print("Successfully saved as WAV.")


def start_serial_listener():
    """Starts listening on the serial port for audio packets."""
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT) as ser:
            print("Waiting for audio stream... (Press Ctrl+C to stop)")

            # Flush any old data in the serial buffer
            ser.flushInput()
            while True:
                # --- Synchronization Step ---
                # 1. Read 1 byte, check if it's HEADER_BYTE_1
                byte1_raw = ser.read(1)
                if not byte1_raw:
                    # This happens on timeout
                    print("T", end="", flush=True)  # Indicate a timeout
                    continue
                if byte1_raw[0] != HEADER_BYTE_1:
                    # Not the start of a packet, keep searching
                    continue
                # 2. Read 1 more byte, check if it's HEADER_BYTE_2
                byte2_raw = ser.read(1)
                if not byte2_raw:
                    continue  # Timeout

                if byte2_raw[0] != HEADER_BYTE_2:
                    # Got 0xFF but not 0xFE, false positive
                    continue
                # --- Payload Step ---
                # If we're here, we found the 0xFFFE header.
                # 3. Read the exact payload size
                data = ser.read(PAYLOAD_SIZE_BYTES)

                if len(data) == PAYLOAD_SIZE_BYTES:
                    # We got the full packet!
                    all_audio_data.append(data)
                    # Print "." to show a successful packet
                    print(".", end="", flush=True)
                    save_audio_wav(data)
                else:
                    # Didn't get the full payload, buffer was incomplete.
                    # This indicates a problem (e.g., serial buffer overrun)
                    # We'll discard this packet and resync.
                    print("x", end="", flush=True)
    except KeyboardInterrupt:
        print("\nShutting down listener...")
        # [FIX] Call save_audio_data() HERE, before the function returns.
        full_data = b"".join(all_audio_data)
        save_audio_wav(full_data, "cool file")


if __name__ == "__main__":
    start_serial_listener()
    # [FIX] Now, this code runs *after* start_serial_listener has returned,
    # and we are guaranteed that save_audio_data() has already been called
    # (if the user pressed Ctrl+C or an error occurred).
