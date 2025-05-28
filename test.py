import cv2
import numpy as np
import glob
import os

# 参数设置
chessboard_size = (9, 6)  # 内角点数量（方格数-1）
square_size = 2.0786  # 棋盘格实际边长（cm）

# 方法1：使用绝对路径（推荐）
image_dir = 'D:/files/pictures'  # 替换为你的实际路径
images = glob.glob(os.path.join(image_dir, '*.jpg')) + \
         glob.glob(os.path.join(image_dir, '*.png'))  # 支持jpg和png格式

# 方法2：使用相对路径（代码和图片同目录）
# images = glob.glob('*.jpg') + glob.glob('*.png')

# 检查是否找到图片
if not images:
    print("错误：未找到任何图片！请检查路径")
    exit()

# 准备标定数据
obj_points = []
img_points = []

# 生成理论角点坐标
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

# 标定过程
for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"警告：无法读取图片 {fname}，已跳过")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        # 亚像素级角点检测
        corners_refined = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        obj_points.append(objp)
        img_points.append(corners_refined)

        # 可视化
        cv2.drawChessboardCorners(img, chessboard_size, corners_refined, ret)
        cv2.imshow('Corners Detection', img)
        cv2.waitKey(500)  # 显示0.5秒

cv2.destroyAllWindows()

# 检查是否有足够数据
if len(obj_points) < 10:
    print(f"警告：仅检测到 {len(obj_points)} 张有效图片，建议至少15张")

# 相机标定
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    obj_points, img_points, gray.shape[::-1], None, None)

# 打印结果
print("\n标定结果：")
print("1. 相机内参矩阵 (K):\n", mtx)
print("2. 畸变系数 (k1,k2,p1,p2,k3):\n", dist.ravel())
print("3. 平均重投影误差 (像素):", ret)

# 保存结果
np.savez("camera_calibration.npz",
         mtx=mtx, dist=dist,
         rvecs=rvecs, tvecs=tvecs)
print("\n标定结果已保存到 camera_calibration.npz")