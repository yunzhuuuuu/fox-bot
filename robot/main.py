import time
import robot.software.audio_processing.pitch_finder as pf
from robot.software.behaviors import RobotBehaviors
import serial
import time


def print_robot_state(fox):
    print("\n================ ROBOT STATE ================")
    print(f"Left speed:       {fox.left_speed}")
    print(f"Right speed:      {fox.right_speed}")
    print(f"Ear angle:        {fox.ear}")
    print(f"Tail angle:       {fox.tail}")
    print(f"Eye brightness:   {fox.eye_brightness}")
    print(f"Left eye array:   {fox.left_eye.current_state}")
    print(f"Right eye array:  {fox.right_eye.current_state}")
    print("Raw bytes:", packet)
    print("=============================================")


if __name__ == "__main__":
    print("Started run...")
    port = "/dev/ttyACM0"
    arduino = serial.Serial(port, 115200)
    time.sleep(1)  # wait for Arduino reset after serial connection
    print("Waking up...")
    button_pressed = 0
    seen_treat = 0
    is_melody = 0
    # is_melody = pf.run_pitch_finder("output_audio.wav", 8)
    fox = RobotBehaviors(button_pressed, seen_treat, is_melody)

    while True:
        print("Starting loop...")
        # recieved data from arduino
        data = arduino.readline().decode()
        if len(data) > 0:
            print("Received: " + data)
        else:
            print("No data...")
        fox.update()
        print("foxbot updated...")
        packet = fox.build_packet()
        arduino.write(packet)
        print("Sent packet...")
        print_robot_state(fox)
        time.sleep(0.01)  # 20 hz
        print("Sleeping...")
