import socket
import time

# Setu[]
ARDUINO_IP = '192.168.137.112' # Arduino IP address
ARDUINO_PORT = 8081 # Must match 'serverPort' of arduino


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
    # start_server()
    time.sleep(1)
    send_data("L")

