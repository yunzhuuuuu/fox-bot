from math import floor
import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()


def process_mouse_event(event, x, y, flags, param):
    print(
        "Color (h=%d,s=%d,v=%d)"
        % (hsv_frame[y, x, 0], hsv_frame[y, x, 1], hsv_frame[y, x, 2])
    )


cv.namedWindow("video_window")
cv.namedWindow("binary_window")
cv.setMouseCallback("video_window", process_mouse_event)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        break

    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # use hue values 0-10 *and* 170-180 to account for wrapping, because
    # that's where red is in hsv space
    binary_image_1 = cv.inRange(hsv_frame, (0, 60, 60), (10, 255, 130))
    binary_image_2 = cv.inRange(hsv_frame, (170, 60, 60), (180, 255, 130))
    binary_image = binary_image_1 + binary_image_2

    moments = cv.moments(binary_image)
    # print(moments)
    if moments["m00"] != 0:
        center_x, center_y = (
            moments["m10"] / moments["m00"],
            moments["m01"] / moments["m00"],
        )

        # print(center_x, ", ", center_y)
        frame = cv.circle(frame, (floor(center_x), floor(center_y)), 5, [0, 255, 0], -1)

    cv.imshow("video_window", frame)
    cv.imshow("binary_window", binary_image)

    if cv.waitKey(1) == ord("q"):
        break


# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
