import socket
import time
import robot.audio_processing.pitch_finder as pf

<<<<<<< HEAD
# Setup
ARDUINO_IP = '192.168.137.67' # Arduino IP address
ARDUINO_PORT = 8081 # Must match 'serverPort' of arduino
=======
# Setup[]
ARDUINO_IP = "192.168.137.112"  # Arduino IP address
ARDUINO_PORT = 8081  # Must match 'serverPort' of arduino
>>>>>>> 27b70cf2ec2f3ef1139ef6a0abd742d54e18434a


def send_data(command):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

        command_bytes = command.encode("utf-8")

        try:
            s.sendto(command_bytes, (ARDUINO_IP, ARDUINO_PORT))
            print(f"Sent: {command}")
            print(f"{command_bytes}")
        except socket.error as e:
            print(f"Error sending data: {e}")


if __name__ == "__main__":
<<<<<<< HEAD
    send_data("L")

=======
    # start_server()
    time.sleep(1)
    is_melody = pf.run_pitch_finder("media/output_audio.wav", 8)
    if is_melody:
        send_data("Active")
>>>>>>> 27b70cf2ec2f3ef1139ef6a0abd742d54e18434a
