# Bytes 1&2 = Angle delta for robot to move 0-360(2 bytes)

import math

# TODO: a function that converts audio amplitude to distance


def law_of_cos(a, b, c):
    cos_val = (b**2 + c**2 - a**2) / (2 * b * c)
    angle_A = math.acos(cos_val)
    return angle_A


def calculate_spin(d1, d2, d3):
    """
    d1, d2, d3: distances from microphones to sound source
    d1: forward mic
    d2: left mic
    d3: right mic
    Returns angle (-180 to 180) to rotate so the robot's "head" points toward the sound source.
    """
    d_max = max(d1, d2, d3)
    # radius of the robot
    r = 10.5  # inches
    spacing = math.sqrt(3) * r

    if d2 == d_max:
        inscribed_a = law_of_cos(d1, spacing, d2)
        angle = math.degrees(2 * inscribed_a)

    elif d1 == d_max:
        inscribed_a = law_of_cos(d3, spacing, d1)
        angle = math.degrees(2 * inscribed_a) + 120

    else:  # d3 == d_max
        inscribed_a = law_of_cos(d1, spacing, d3)
        angle = math.degrees(2 * inscribed_a) + 240

    return angle


if __name__ == "__main__":
    d1 = 70
    d2 = 85
    d3 = 70

    angle = calculate_spin(d1, d2, d3)
    print(f"\nSpin angle: {angle:.2f} degrees")
