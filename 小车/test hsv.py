import cv2
import numpy as np

# 定义回调函数
def empty(a):
    pass

# 创建滑条窗口
cv2.namedWindow('HSV Slider')


# 创建滑条，初始值设为默认值
cv2.createTrackbar('Hue Min', 'HSV Slider', 0, 179, empty)
cv2.createTrackbar('Hue Max', 'HSV Slider', 179, 179, empty)
cv2.createTrackbar('Sat Min', 'HSV Slider', 0, 255, empty)
cv2.createTrackbar('Sat Max', 'HSV Slider', 255, 255, empty)
cv2.createTrackbar('Val Min', 'HSV Slider', 0, 255, empty)
cv2.createTrackbar('Val Max', 'HSV Slider', 255, 255, empty)

# 初始化摄像头
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("无法打开摄像头")
    exit()

while True:
    # 读取一帧
    ret, frame = camera.read()
    if not ret:
        print("无法获取视频帧")
        break
    
    # 获取滑条的值
    h_min = cv2.getTrackbarPos('Hue Min', 'HSV Slider')
    h_max = cv2.getTrackbarPos('Hue Max', 'HSV Slider')
    s_min = cv2.getTrackbarPos('Sat Min', 'HSV Slider')
    s_max = cv2.getTrackbarPos('Sat Max', 'HSV Slider')
    v_min = cv2.getTrackbarPos('Val Min', 'HSV Slider')
    v_max = cv2.getTrackbarPos('Val Max', 'HSV Slider')
    
    # 转换到HSV空间并应用阈值
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([h_min, s_min, v_min])
    upper_hsv = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    # 显示结果
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result', result)
    
    # 按'q'键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
camera.release()
cv2.destroyAllWindows()
