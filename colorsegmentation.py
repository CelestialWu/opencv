import cv2
import numpy as np

target_color_rgb=[
	(30,67,109), #blue
	(187,68,47), #red
]

img=cv2.imread("test1.jpg")
hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)


mask_total=None

for rgb in target_color_rgb:
	rgb1=np.uint8([[list(rgb)]])
	hsv1=cv2.cvtColor(rgb1,cv2.COLOR_RGB2HSV)[0][0]
	
	lower=np.array([max(hsv1[0]-10,0),50,50])
	upper=np.array([min(hsv1[0]+10,179),225,225])

	mask=cv2.inRange(hsv,lower,upper)

	mask_total=mask if mask_total is None else cv2.bitwise_or(mask_total,mask)

result=cv2.bitwise_and(img,img,mask=mask_total)

cv2.imwrite("mask_output.png", mask_total)
cv2.imwrite("result_output.png", result)

