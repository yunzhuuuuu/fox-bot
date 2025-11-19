class EyeDisplay:

    def eye_to_bytes(self, eye_strings):
        """_summary_

        Args:
            eye_strings (_type_): _description_

        Returns:
            _type_: _description_
        """
        flattened_string = "".join([str(bit) for line in eye_strings for bit in line])
        print(flattened_string)
        eye_bytes = int(flattened_string, 2).to_bytes(8, byteorder="big")
        return eye_bytes

    def eye_with_position(self, position):
        """
        Generates an array with 1's in a circle-like shape at a given coordinate.

        Args:
            position (tuple): x and y coordinates of upper left corner of circle

        Returns:
            2D array of 0's and 1's representing the eye
        """

        x = position[0]
        y = position[1]

        eye = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

        for row in range(8):
            if row == y or row == y + 4:  # first and last rows (3 pixels)
                for col in range(8):
                    if col > x and col < x + 4:
                        eye[row][col] = 1
            elif row > y and row < y + 4:  # middle rows (5 pixels)
                for col in range(8):
                    if col >= x and col <= x + 4:
                        eye[row][col] = 1

        return eye

    def eye_rotate_clockwise(self):  # true for clockwise, false for counterclockwise
        positions = [
            (0, 1),
            (1, 0),
            (2, 0),
            (3, 1),
            (3, 2),
            (2, 3),
            (1, 3),
            (0, 2),
        ]

        return (self.eye_with_position(position) for position in positions)

    blink = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]


myEye = EyeDisplay()


print(myEye.eye_to_bytes(myEye.eye_with_position((2, 2))))
