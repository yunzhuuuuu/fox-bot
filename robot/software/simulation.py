import time
from robot.software.behaviors import RobotBehaviors


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
    print("=============================================")


def print_packet(packet):
    print("Raw bytes:      ", packet)
    print("Hex:            ", packet_to_hex(packet))
    print("Decimal bytes:  ", packet_to_dec(packet))
    print("---------------------------------------------")


if __name__ == "__main__":
    button_pressed = 0
    seen_treat = 1
    fox = RobotBehaviors(button_pressed, seen_treat)

    # Run simulation
    while True:
        fox.update()
        packet = fox.build_packet()

        print_robot_state(fox)
        print_packet(packet)

        time.sleep(0.05)
