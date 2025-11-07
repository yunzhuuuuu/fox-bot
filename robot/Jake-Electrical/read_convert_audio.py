import serial
import wave
import numpy as np

# Audio Format Settings
SERIAL_PORT = 'COM10' # UPDATE THIS to match actual Arduino's port
BAUD_RATE = 1000000 # Must match SERIAL_BAUD_RATE in Arduino
SERIAL_TIMEOUT = 1 # Seconds

HEADER_BYTE_1 = 0xFF
HEADER_BYTE_2 = 0xFE
# 729 samples * 2 bytes/sample = 1458 bytes
PAYLOAD_SIZE_BYTES = 1458 

CHANNELS = 3 # Must match NUM_CHANNELS in Arduino
SAMPLE_RATE = 7500 # Must match SAMPLE_RATE in Arduino
SAMPLE_WIDTH_BYTES = 2 # 16-bit audio (int16_t)

OUTPUT_FILENAME = "output_audio.raw"
OUTPUT_WAV_FILENAME = "output_audio.wav" # Make sure 'media' folder exists


all_audio_data = []

def save_audio_wav():
    """
    Saves all collected audio data (payloads only) to a .wav file.
    """
    print(f"\nSaving audio chunks directly to {OUTPUT_WAV_FILENAME}...")
 
    # Combine all binary chunks into one big bytes object
    full_data = b''.join(all_audio_data)
    samples = np.frombuffer(full_data, dtype='<i2')  # little-endian('<') 16-bit('i2') signed int

    # Reshape into 3-column array (3 mics)
    if len(samples) % 3 != 0:
        samples = samples[: (len(samples) // 3) * 3]
    samples = samples.reshape(-1, 3)

    # Separate into three channels
    mic1, mic2, mic3 = samples[:, 0], samples[:, 1], samples[:, 2]

    # Internal function to save one channel to WAV
    def save_single_channel(filename, data):
        with wave.open(filename, "wb") as f_out:
            f_out.setnchannels(1)
            f_out.setframerate(SAMPLE_RATE)
            f_out.setsampwidth(SAMPLE_WIDTH_BYTES)
            f_out.writeframes(data.tobytes())

    # Save each mic
    save_single_channel("mic1_output.wav", mic1)
    save_single_channel("mic2_output.wav", mic2)
    save_single_channel("mic3_output.wav", mic3)

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
                    print("T", end="", flush=True) # Indicate a timeout
                    continue
                if byte1_raw[0] != HEADER_BYTE_1:
                    # Not the start of a packet, keep searching
                    continue
                # 2. Read 1 more byte, check if it's HEADER_BYTE_2
                byte2_raw = ser.read(1)
                if not byte2_raw:
                    continue # Timeout

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
                else:
                    # Didn't get the full payload, buffer was incomplete.
                    # This indicates a problem (e.g., serial buffer overrun)
                    # We'll discard this packet and resync.
                    print("x", end="", flush=True)
    except KeyboardInterrupt:
        print("\nShutting down listener...")
        # [FIX] Call save_audio_data() HERE, before the function returns.
        save_audio_wav()

if __name__ == "__main__":
    start_serial_listener()
    # [FIX] Now, this code runs *after* start_serial_listener has returned,
    # and we are guaranteed that save_audio_data() has already been called
    # (if the user pressed Ctrl+C or an error occurred).
