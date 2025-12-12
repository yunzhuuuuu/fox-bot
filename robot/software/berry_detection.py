from math import floor
import numpy as np
import cv2 as cv


class BerryDetection:
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")

    def __del__(self):
        self.cap.release()

    def get_berry_position(self):
        """
        Detect position of red object.

        Returns:
            (int, int) or None: (x,y) position of object, or None if no object is detected
        """

        ret, frame = self.cap.read()
        # if frame is read correctly ret is True
        if not ret:
            return None

        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # use hue values 0-10 *and* 170-180 to account for wrapping, because
        # that's where red is in hsv space
        binary_image_1 = cv.inRange(hsv_frame, (0, 60, 100), (10, 255, 255))
        binary_image_2 = cv.inRange(hsv_frame, (170, 60, 100), (180, 255, 255))
        binary_image = binary_image_1 + binary_image_2

        moments = cv.moments(binary_image)
        if moments["m00"] != 0:
            center_x, center_y = (
                moments["m10"] / moments["m00"],
                moments["m01"] / moments["m00"],
            )
            return (center_x, center_y)

        return None
