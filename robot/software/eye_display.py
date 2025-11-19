class EyeDisplay:

    def eye_to_bytes(self, eye_lists):
        """_summary_

        Args:
            eye_strings (_type_): _description_

        Returns:
            _type_: _description_
        """
        eye_bytes = []
        for line in eye_lists:
            flattened_string = "".join([str(bit) for bit in line])
            print(flattened_string)
            eye_bytes.append(int(flattened_string, 2).to_bytes(1, byteorder="big"))
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

    def eye_rotate(self, clockwise):  # true for clockwise, false for counterclockwise
        """
        Generates a series of eye arrays with pupil positions in a circle.

        Args:
            clockwise (boolean): Boolean representing whether it should go clockwise or counterclockwise.

        Returns:
            list<list<list<boolean>>>: List of 2d lists of booleans representing eyes.
        """
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

        if clockwise:
            return (self.eye_with_position(position) for position in positions)
        return (self.eye_with_position(position) for position in reversed(positions))

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

    sleeping = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    happy = reversed(sleeping)

    heart_left = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
    ]

    heart_right = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
    ]
