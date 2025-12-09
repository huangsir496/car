import cv2
import time

# 全局变量存储摄像头对象
camera = None

# 默认配置参数
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_FPS = 30
DEFAULT_CAMERA_INDEX = 0

def init_camera(camera_index=DEFAULT_CAMERA_INDEX, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, fps=DEFAULT_FPS):
    """初始化摄像头"""
    global camera
    
    # 尝试打开摄像头
    camera = cv2.VideoCapture(camera_index)
    
    # 检查摄像头是否成功打开
    if not camera.isOpened():
        print(f"错误: 无法打开摄像头索引 {camera_index}")
        return False
    
    # 确保使用MJPG格式
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    print("已设置摄像头格式为MJPG")
    
    # 设置基本参数
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    camera.set(cv2.CAP_PROP_FPS, fps)
    
    print("摄像头初始化成功")
    print(f"设置分辨率: {width}x{height}")
    print(f"设置帧率: {fps}")
    return True


def get_frame():
    """获取一帧图像"""
    global camera
    
    if camera is None:
        print("错误: 摄像头未初始化")
        return None
    
    # 读取图像帧
    ret, frame = camera.read()
    
    if not ret:
        print("无法获取图像帧")
        return None
    
    return frame


def release_camera():
    """释放摄像头资源"""
    global camera
    
    if camera is not None:
        camera.release()
        camera = None
        print("摄像头资源已释放")

