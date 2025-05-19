import cv2
import numpy as np

mask=cv2.imread("mask_output.png",cv2.IMREAD_GRAYSCALE)

contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

image=cv2.imread('color_test.jpg')
output=image.copy()

for cnt in contours:
	if cv2.contourArea(cnt)<100:
		continue
	
	rect=cv2.minAreaRect(cnt)
	box=cv2.boxPoints(rect)
	box = box.astype(np.int32)
	cv2.drawContours(output,[box],0,(0,255,0),2)
	
	epsilon=0.01*cv2.arcLength(cnt,True)
	approx=cv2.approxPolyDP(cnt,epsilon,True)
	cv2.drawContours(output, [approx], 0, (0, 0, 255), 2)

cv2.imwrite('contour_fitted.png', output)
print("图像已保存为 contour_fitted.png")

