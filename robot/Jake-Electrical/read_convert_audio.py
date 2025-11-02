import socket
import sys
import atexit
import wave
import time

# Setu[]
HOST_IP = '0.0.0.0' # All network interfaces
HOST_PORT = 8080 # Must match 'serverPort' of arduino
BUFFER_SIZE = 1460 # Max packet size to receive
OUTPUT_FILENAME = "output_audio.raw"

all_audio_data = []

def save_audio_data():
    """Saves all collected audio data to a raw file."""
    try:
        with open(OUTPUT_FILENAME, 'wb') as f:
            for data_chunk in all_audio_data:
                f.write(data_chunk)
    except Exception as e:
        print(f"Error saving file: {e}")

def convert_wav():
    """Converts .raw file to .wave audio file."""
    CHANNELS = 1
    SAMPE_RATE = 8000
    with open(OUTPUT_FILENAME, "rb") as f_in:
        data = f_in.read()
        with wave.open("output_audio.wav", "wb") as f_out:
            f_out.setnchannels(1) # Microphone numbers
            f_out.setframerate(3875) # Sampling rate
            f_out.setsampwidth(2) # Number of bytes
            f_out.writeframesraw(data) # Write data to file

def start_server():
    """Starts the UDP server to listen for audio packets."""

    atexit.register(save_audio_data)

    # Create a socket with IPV4 and UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # Bind the socket to the host and port
            s.bind((HOST_IP, HOST_PORT))
            
            print(f"UDP Server started at {HOST_IP} on port {HOST_PORT} ---")
            print("Waiting for audio stream...")

            while True:
                data, addr = s.recvfrom(BUFFER_SIZE)
                
                all_audio_data.append(data)

                # Print "." to show packet
                print(".", end="", flush=True)

        except KeyboardInterrupt:
            print("\nShutting down server...")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # start_server()
    time.sleep(3)
    convert_wav()