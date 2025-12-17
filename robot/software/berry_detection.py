from math import floor
import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    raise Exception("you suck")
else:
    print("opened camera")


class BerryDetection:

    def get_darkness(self):
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            return None

        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        _, _, v = cv.split(hsv_frame)
        print("brightness:", np.mean(v))
        return np.mean(v) < 100

    def get_berry_position(self):
        """
        Detect position of red object.

        Returns:
            (int, int) or None: (x,y) position of object, or None if no object is detected
        """
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            return None

        frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # use hue values 0-10 *and* 170-180 to account for wrapping, because
        # that's where red is in hsv space
        binary_image_1 = cv.inRange(hsv_frame, (0, 60, 60), (10, 255, 130))
        binary_image_2 = cv.inRange(hsv_frame, (170, 60, 60), (180, 255, 130))
        binary_image = binary_image_1 + binary_image_2

        moments = cv.moments(binary_image)
        if moments["m00"] != 0:
            center_x, center_y = (
                moments["m10"] / moments["m00"],
                moments["m01"] / moments["m00"],
            )
            return (center_x, center_y)

        return None
