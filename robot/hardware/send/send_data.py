import socket
import time
import robot.software.audio_processing.pitch_finder as pf
import robot.software.idle_states as idle
# Setup[]
ARDUINO_IP = "192.168.137.112"  # Arduino IP address
ARDUINO_PORT = 8081  # Must match 'serverPort' of arduino


def send_data(command):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

        # command_bytes = command.encode("utf-8")
        command_bytes = command

        try:
            s.sendto(command_bytes, (ARDUINO_IP, ARDUINO_PORT))
            print(f"Sent: {command}")
            print(f"{command_bytes}")
        except socket.error as e:
            print(f"Error sending data: {e}")


if __name__ == "__main__":
    # start_server()
    time.sleep(1)
    # is_melody = pf.run_pitch_finder("output_audio.wav", 8)
    # if is_melody:
    #     send_data("Active")
    fox = idle.RobotIdleState()
    fox.update()
    array = fox.build_packet() 
    # b'\x00\x00\x00X{\x01\x00\x00\x18<<\x18\x00\x00'
    send_data(array)
