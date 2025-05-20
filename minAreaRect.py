import cv2
import numpy as np

image = cv2.imread("test2.png")
if image is None:
    exit()

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 30, 255])

mask = cv2.inRange(hsv, lower_white, upper_white)

kernel = np.ones((7, 7), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

cv2.imwrite("mask_debug.png", mask)

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

output = image.copy()
corner_boxes = []

h, w = image.shape[:2]
corner_regions = [
    (w // 4, h // 4, 2 * w // 4, 2 * h // 4),
    (2 * w // 4, h // 4, 3 * w // 4, 2 * h // 4),
    (w // 4, 2 * h // 4, 2 * w // 4, 3 * h // 4),
    (2 * w // 4, 2 * h // 4, 3 * w // 4, 3 * h // 4)
]

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 50 or area > 5000:
        continue

    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    center = np.mean(box, axis=0)

    is_corner = any(
        (x1 <= center[0] <= x2) and (y1 <= center[1] <= y2)
        for (x1, y1, x2, y2) in corner_regions
    )

    if is_corner:
        corner_boxes.append(box)
        cv2.drawContours(output, [box], 0, (0, 255, 0), 2)

        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        cv2.drawContours(output, [approx], 0, (0, 0, 255), 2) 

cv2.imwrite("white_corners.png", output)
