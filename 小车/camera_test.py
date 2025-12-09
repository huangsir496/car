import cv2
import time

# 测试函数
def test_camera(backend=None, fourcc=None):
    """测试不同参数组合下的摄像头打开情况"""
    
    for idx in range(2):  # 测试前2个索引
        print(f"\n=== 测试摄像头索引 {idx} ===")
        
        # 尝试不同的参数组合
        for use_backend in [True, False] if backend is None else [True]:
            for use_fourcc in [True, False] if fourcc is None else [True]:
                
                cap = None
                try:
                    if use_backend and backend is not None:
                        cap = cv2.VideoCapture(idx, backend)
                        print(f"使用后端 {backend} 打开摄像头")
                    else:
                        cap = cv2.VideoCapture(idx)
                        print(f"使用默认后端打开摄像头")
                    
                    if cap.isOpened():
                        print("✓ 摄像头成功打开")
                        
                        if use_fourcc and fourcc is not None:
                            cap.set(cv2.CAP_PROP_FOURCC, fourcc)
                            print(f"设置格式为 {fourcc}")
                        
                        # 尝试读取一帧
                        ret, frame = cap.read()
                        if ret:
                            print(f"✓ 成功读取一帧，尺寸: {frame.shape}")
                        else:
                            print("✗ 无法读取帧")
                            
                        # 获取实际参数
                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        actual_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                        fourcc_str = "".join([chr((actual_fourcc >> 8 * i) & 0xFF) for i in range(4)])
                        
                        print(f"实际分辨率: {width}x{height}")
                        print(f"实际帧率: {fps}")
                        print(f"实际格式: {fourcc_str}")
                        
                        # 释放摄像头
                        cap.release()
                        return True
                    else:
                        print("✗ 无法打开摄像头")
                        if cap is not None:
                            cap.release()
                except Exception as e:
                    print(f"✗ 发生错误: {e}")
                    if cap is not None:
                        cap.release()

# 测试不同的后端
backends = [
    None,  # 默认后端
    cv2.CAP_V4L,  # V4L后端
    cv2.CAP_V4L2  # V4L2后端
]

# 测试不同的格式
fourccs = [
    None,  # 默认格式
    cv2.VideoWriter_fourcc(*'MJPG'),  # MJPG格式
    cv2.VideoWriter_fourcc(*'YUYV'),  # YUYV格式
    cv2.VideoWriter_fourcc(*'H264')   # H264格式
]

# 主测试循环
print("开始摄像头兼容性测试...")
print(f"OpenCV版本: {cv2.__version__}")

success = False

# 尝试所有后端和格式组合
for backend in backends:
    for fourcc in fourccs:
        if test_camera(backend, fourcc):
            success = True
            break
    if success:
        break

if not success:
    print("\n=== 测试结果 ===")
    print("所有测试组合都无法打开摄像头！")
    print("可能的原因:")
    print("1. 摄像头硬件问题")
    print("2. 驱动程序问题")
    print("3. OpenCV版本兼容性问题")
    print("4. 权限问题")
else:
    print("\n=== 测试结果 ===")
    print("找到了可用的摄像头参数组合！")
