def eye_with_position(x, y):

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


blink = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]


test_eye = eye_with_position(-1, 3)

for row in test_eye:
    print(row)
