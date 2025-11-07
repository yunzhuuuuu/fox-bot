import serial # Replaces 'socket'
import sys
import atexit
import wave
import time

# --- Serial Port Settings ---
# !!! UPDATE THIS to match your Arduino's port !!!
# Linux: /dev/ttyACM0 or /dev/ttyUSB0
# macOS: /dev/cu.usbmodemXXXX
# Windows: COM3, COM4, etc.
SERIAL_PORT = 'COM16' 
BAUD_RATE = 1000000 # Must match SERIAL_BAUD_RATE in Arduino
SERIAL_TIMEOUT = 1 # Seconds

# --- Arduino Packet Settings ---
HEADER_BYTE_1 = 0xFF
HEADER_BYTE_2 = 0xFE
# 729 samples * 2 bytes/sample = 1458 bytes
PAYLOAD_SIZE_BYTES = 1458 

# --- Output File Settings ---
OUTPUT_FILENAME = "output_audio.raw"
OUTPUT_WAV_FILENAME = "output_audio.wav" # Make sure 'media' folder exists

# --- Audio Format Settings ---
CHANNELS = 3 # Must match NUM_CHANNELS in Arduino
SAMPLE_RATE = 7500 # Must match SAMPLE_RATE in Arduino
SAMPLE_WIDTH_BYTES = 2 # 16-bit audio (int16_t)

all_audio_data = []

def save_audio_data():
    """Saves all collected audio data (payloads only) to a raw file."""
    if not all_audio_data:
        print("\nNo audio data was collected.")
        return

    print(f"\nSaving {len(all_audio_data)} audio chunks to {OUTPUT_FILENAME}...")
    try:
        with open(OUTPUT_FILENAME, 'wb') as f:
            for data_chunk in all_audio_data:
                f.write(data_chunk)
        print(f"Successfully saved raw audio.")
    except Exception as e:
        print(f"Error saving file: {e}")

def convert_wav():
    """Converts .raw file to .wave audio file."""
    print(f"Converting {OUTPUT_FILENAME} to {OUTPUT_WAV_FILENAME}...")
    try:
        with open(OUTPUT_FILENAME, "rb") as f_in:
            data = f_in.read()
            if not data:
                print("Raw file is empty, skipping WAV conversion.")
                return

            with wave.open(OUTPUT_WAV_FILENAME, "wb") as f_out:
                f_out.setnchannels(CHANNELS)
                f_out.setframerate(SAMPLE_RATE)
                f_out.setsampwidth(SAMPLE_WIDTH_BYTES)
                f_out.writeframesraw(data) # Write data to file
            print("Successfully converted to WAV.")
            
    except FileNotFoundError:
        print(f"Error: Raw file not found at {OUTPUT_FILENAME}.")
    except Exception as e:
        print(f"Error during WAV conversion: {e}")


def start_serial_listener():
    """Starts listening on the serial port for audio packets."""

    # [FIX] We will call save_audio_data() manually on exit, not with atexit.
    # atexit.register(save_audio_data)

    # Create a serial port object
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT) as ser:
            print(f"Serial listener started on {SERIAL_PORT} at {BAUD_RATE} baud ---")
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

    except serial.SerialException as e:
        print(f"\n--- Serial Error ---")
        print(f"Could not open port '{SERIAL_PORT}'.")
        print("Please check the following:")
        print("  1. Is the Arduino plugged in?")
        print(f"  2. Is '{SERIAL_PORT}' the correct port name?")
        print("  3. Is another program (like the Arduino IDE Serial Monitor) using the port?")
        print(f"Error details: {e}")
    except KeyboardInterrupt:
        print("\nShutting down listener...")
        # [FIX] Call save_audio_data() HERE, before the function returns.
        save_audio_data()
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        # [FIX] Also save on any other unexpected error
        save_audio_data()

if __name__ == "__main__":
    start_serial_listener()
    # [FIX] Now, this code runs *after* start_serial_listener has returned,
    # and we are guaranteed that save_audio_data() has already been called
    # (if the user pressed Ctrl+C or an error occurred).
    convert_wav()