import time
from robot.software.idle_states import RobotIdleState


def packet_to_hex(packet):
    return " ".join(f"{b:02X}" for b in packet)


def packet_to_dec(packet):
    return [b for b in packet]


def print_robot_state(fox):
    print("\n================ ROBOT STATE ================")
    print(f"Speed:          {fox.speed}")
    print(f"Spin:           {fox.spin}")
    print(f"Ear angle:      {fox.ear}")
    print(f"Tail angle:     {fox.tail}")
    print(f"Eye brightness: {fox.eye_brightness}")
    print(f"Eye array:      {fox.eye_object.current_state}")
    print("=============================================")


def print_packet(packet):
    print("Raw bytes:      ", packet)
    print("Hex:            ", packet_to_hex(packet))
    print("Decimal bytes:  ", packet_to_dec(packet))
    print("---------------------------------------------")


if __name__ == "__main__":
    fox = RobotIdleState()

    # Run simulation
    while True:
        fox.update()
        packet = fox.build_packet()

        print_robot_state(fox)
        print_packet(packet)

        time.sleep(0.05)
