# combines all robot components behavior for the idle state

# return array:
# Serial Data format: (14 byte packet)
# Byte 0 = Speed to set motors to 0-255(byte)
# Bytes 1&2 = Angle delta for robot to move -180-180(2 bytes)
# Byte 3 = Servo angle for ears 0-180(byte)
# Byte 4 = Servo angle for the tail 0-180(byte)
# Bytes 6-13 = Array for the eyes

def sleep():
    """
    docstring
    """
    return None # actually an array

def chase_tail():
    """
    docstring
    """
    return None

# more states

def run_idle():
    # randomly call one of the above states
    return None
