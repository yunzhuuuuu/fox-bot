import time
from robot.software.behaviors import RobotBehaviors
from robot.software.behavior_manager import StateManager


def packet_to_hex(packet):
    return " ".join(f"{b:02X}" for b in packet)


def packet_to_dec(packet):
    return [b for b in packet]


def print_robot_state(fox):
    print("\n================ ROBOT STATE ================")
    print(f"Left speed:       {fox.left_speed}")
    print(f"Right speed:      {fox.right_speed}")
    print(f"Ear angle:        {fox.ear}")
    print(f"Tail angle:       {fox.tail}")
    print(f"Eye brightness:   {fox.eye_brightness}")
    print(f"Left eye array:   {fox.left_eye.current_state}")
    print(f"Right eye array:  {fox.right_eye.current_state}")
    print(f"State:            {fox.state}")
    print(f"Behavior:         {fox.behavior}")
    print("=============================================")


def print_packet(packet):
    print("Raw bytes:      ", packet)
    print("Hex:            ", packet_to_hex(packet))
    print("Decimal bytes:  ", packet_to_dec(packet))
    print("---------------------------------------------")


if __name__ == "__main__":
    button_pressed = 0
    seen_treat = 0
    heard_melody = 0
    state_manager = StateManager(button_pressed, seen_treat, heard_melody)
    fox = RobotBehaviors(state_manager)

    # Run simulation
    while True:
        state_manager.update_state()
        fox.update_bahavior()
        fox.behavior()
        packet = fox.build_packet()
        print_robot_state(fox)
        time.sleep(0.02)  # 50 hz
