import time
from robot.software.behaviors import RobotBehaviors
from robot.software.behavior_manager import StateManager
import serial
import time


def print_robot_state(fox, state_manager):
    print("\n================ ROBOT STATE ================")
    print(f"Left speed:       {fox.left_speed}")
    print(f"Right speed:      {fox.right_speed}")
    print(f"Ear angle:        {fox.ear}")
    print(f"Tail angle:       {fox.tail}")
    print(f"Eye brightness:   {fox.eye_brightness}")
    print(f"Left eye array:   {fox.left_eye.current_state}")
    print(f"Right eye array:  {fox.right_eye.current_state}")
    print(f"State:            {fox.state}")
    print(f"Button state:     {state_manager.button_pressed}")
    print(f"Melody:           {state_manager.heard_melody}")
    print(f"Word command:     {state_manager.command}")
    print("Raw bytes:", packet)
    print("=============================================")


if __name__ == "__main__":
    print("Started run...")
    port = "/dev/ttyACM0"
    arduino = serial.Serial(port, 115200, timeout=0.1)
    time.sleep(1)  # wait for Arduino reset after serial connection
    print("Waking up...")
    state_manager = StateManager(arduino)
    fox = RobotBehaviors(state_manager)

    try:
        while True:
            print("Starting loop...")
            # recieved data from arduino
            # data = arduino.readline().decode()
            # if len(data) > 0:
            #     print("Received: " + data)
            # else:
            #     print("No data...")

            state_manager.update_state()
            fox.update_behavior()
            fox.behavior()
            print("foxbot updated...")

            packet = fox.build_packet()
            arduino.write(packet)
            print("Sent packet...")

            print_robot_state(fox, state_manager)
            time.sleep(0.02)  # 50 hz
            print("Sleeping...")
    except KeyboardInterrupt:
        print("STOPPING...")
        fox.left_speed = 0
        fox.right_speed = 0

        packet = fox.build_packet()
        arduino.write(packet)
