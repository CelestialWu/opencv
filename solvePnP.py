import cv2
import numpy as np

#相机标定内参
cameraMatrix=np.array([[1.28866129e+03,0.00000000e+00,6.44996317e+02],
                       [0.00000000e+00,1.28964948e+03,8.20530936e+02],
                       [0.00000000e+00,0.00000000e+00,1.00000000e+00]])

distCoeffs=np.array([9.75592964e-02,-3.69668144e-01,-1.22385649e-03,3.13308344e-04,3.50478819e-01])

#正方形
objectPoints = np.array([[0, 0, 0],
                         [50, 0, 0],
                         [50, 50, 0],
                         [0, 50, 0]], dtype=np.float32)

#坐标轴绘制
def draw_axes(img, rvec, tvec):
    axis = np.float32([[0,0,0],
                       [60, 0, 0],
                       [0, 60, 0],
                       [0, 0, 60]])  # XYZ三轴
    imgpts, _ = cv2.projectPoints(axis, rvec, tvec, cameraMatrix, distCoeffs)#

    origin = tuple(imgpts[0].ravel().astype(int))  # 这是 (0, 0, 0) 投影结果
    x_end = tuple(imgpts[1].ravel().astype(int))
    y_end = tuple(imgpts[2].ravel().astype(int))
    z_end = tuple(imgpts[3].ravel().astype(int))

    img = cv2.line(img, origin, x_end, (0, 0, 255), 3)  # X 红
    img = cv2.line(img, origin, y_end, (0, 255, 0), 3)  # Y 绿
    img = cv2.line(img, origin, z_end, (255, 0, 0), 3)  # Z 蓝
    cv2.circle(img, origin, 5, (0, 255, 255), -1)  # 原点 黄
    return img

#
def sort_corners(corners):
    center = np.mean(corners, axis=0)#几何中心
    angles = np.arctan2(corners[:,1] - center[1], corners[:,0] - center[0])#角点和中心点的相对坐标
    return corners[np.argsort(-angles)]  # 按顺时针排序后的角点数组

#读取视频
cap=cv2.VideoCapture("video.mp4")
#创建一个视频写入器
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break
        

    lower_black = np.array([0, 0, 0])  # 纯黑
    upper_black = np.array([180, 255, 160])  # 接近黑（灰）值

    # 先转 HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 提取黑色区域
    mask = cv2.inRange(hsv, lower_black, upper_black)
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    target_corners = None
    frame_center = np.array([width // 4, height // 3])

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        cv2.imshow("mask_debug.png", mask)
        if len(approx) >= 3 and cv2.isContourConvex(approx):
            area = cv2.contourArea(approx)
            centroid = np.mean(approx.reshape(-1, 2), axis=0)

            if 5000 < area < 1000000 and np.linalg.norm(centroid - frame_center) <400:
                    if area > max_area:
                        max_area = area
                        target_corners = approx

    if target_corners is not None:
        # 排序角点：左上->右上->右下->左下（按顺时针）
        corners = target_corners.reshape(-1, 2).astype(np.float32)
        if len(corners) >= 4:
            sorted_corners = sort_corners(corners)  # 使用极坐标排序代替原sort_key
            imgp = np.array(sorted_corners, dtype=np.float32)
            objp = objectPoints
            flag = cv2.SOLVEPNP_ITERATIVE
        elif len(corners) == 3:
            imgp = np.array(corners, dtype=np.float32)
            objp = objectPoints[:3]
            flag = cv2.SOLVEPNP_P3P
        else:
            imgp = objp = None
        if imgp is not None:
            success, rvec, tvec = cv2.solvePnP(objectPoints, imgp, cameraMatrix, distCoeffs)
            if success:
            # 画坐标轴用于验证
                for i in range(4):
                    pt1 = tuple(imgp[i].astype(int))
                    pt2 = tuple(imgp[(i + 1) % 4].astype(int))
                    frame = cv2.line(frame, pt1, pt2, (0, 255, 255), 2)
                frame = draw_axes(frame, rvec, tvec)
                cv2.imshow("box", frame)

                reproj, _ = cv2.projectPoints(objectPoints, rvec, tvec, cameraMatrix, distCoeffs)


    cv2.imshow("pose", frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
