#不需要cv2，因为只需要处理图像，树莓派不显示这玩意
import numpy as np
import time   
import math


# 从配置文件导入配置参数
from config import (
    CAMERA_CONFIG,       # 相机参数配置
    VISION_CONFIG,       # 视觉处理配置
    COLOR_RANGES,        # 颜色HSV阈值范围配置
    ELECTRONIC_CONTROL_CONFIG  # 电控系统通信配置
)

from camera_capture import init_camera, get_frame # 相机捕获模块
from object_detection import ObjectDetector  # 目标检测模块



# 配置队伍颜色

team_color = "red"


ball_info = [0, 0, 0]  # 默认[水平角度,垂直角度,距离]#垂直角度是刚刚新添加上去的
safe_zone_angle = 0  # 初始化安全区角度为0
safe_zone_distance = 0  # 初始化安全区距离为0
# 初始化相机
camera_init_success = init_camera()
if not camera_init_success:
    print("相机初始化失败，但程序将继续运行串口通信部分")

# 创建目标检测器对象，用于识别球体和安全区域
detector = ObjectDetector()

# 初始化串口通信

try:
    # 从配置中获取串口参数
    serial_port = "/dev/ttyS0" # 从配置文件读取串口设备路径
    baud_rate = 9600  # 从配置文件读取波特率
    timeout = 1   #让它初始化完成后再进行识别，防止乱码
          
    
    # 打开串口，显式设置所有参数
    ser = serial.Serial(
        port=serial_port, 
        baudrate=baud_rate, 
        timeout=0.5
    )
    
    # 检查串口是否成功打开
    if ser.is_open:
        print(f"串口已打开")
        
        serial_enabled = True  # 标记串口可用
    else:
        print(f"串口但未打开")
        serial_enabled = False

except Exception as e:
    
    print(f"无法打开串口: {e}")
    ser = None
    serial_enabled = False

# 主循环：不断处理视频帧和串口命令
while True:
    try:
        # 从相机获取一帧图像
        frame = get_frame()
        
        # 检查串口是否可用
        if serial_enabled and ser is not None:
            try:
                date = ser.readline().decode('utf-8').strip() #读取
                time.sleep(0.05)#等待0.05秒，确保数据完整
                
                if not date:
                    default_response = "[0,0,0]"#初始化回复
                    ser.write(default_response.encode('utf-8'))
                    print(f"未识别命令，发送默认响应: {default_response}")  
                
                elif "[FindTeamColor]" in date:   
                    target_color = team_color  # 首先使用队伍颜色
                    balls = []
                    ball_info = [0, 0, 0]  # 默认[水平角度,垂直角度,距离]
                    if frame is not None:
                        balls, mask = detector.detect_color(frame, target_color)
                    
                    if balls:
                        # 找出最近的球（根据距离排序）
                        closest_ball = min(balls, key=lambda x: x[2])
                        cx, cy, distance, _ = closest_ball  # 解包：中心x坐标、中心y坐标、距离（毫米），多加一点忽略像素直径
                        distance_cm = distance / 10.0  # 转换为厘米
                        
                        # 计算角度
                        img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心点x坐标
                        img_center_y = CAMERA_CONFIG["resolution"][1] / 2  # 图像中心点y坐标
                        
                        # 水平角度计算
                        horizontal_offset = cx - img_center_x  # 水平方向偏移
                        fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # 水平视场角
                        angle_per_pixel_horizontal = fov_horizontal / CAMERA_CONFIG["resolution"][0]  # 每像素对应的水平角度
                        horizontal_angle = horizontal_offset * angle_per_pixel_horizontal  # 计算水平角度
                        
                        # 垂直角度计算
                        vertical_offset = img_center_y - cy  # 垂直方向偏移（上为正，下为负）
                        fov_vertical = CAMERA_CONFIG.get("vertical_fov", 45)  # 垂直视场角
                        angle_per_pixel_vertical = fov_vertical / CAMERA_CONFIG["resolution"][1]  # 每像素对应的垂直角度
                        vertical_angle = vertical_offset * angle_per_pixel_vertical  # 计算垂直角度
                        
                        ball_info = [int(horizontal_angle), int(vertical_angle), int(distance_cm)]
                    
                    # 按照指定格式构建响应数据：[水平角度,垂直角度,距离]
                    response_data = f"[{ball_info[0]},{ball_info[1]},{ball_info[2]}]"
                    ser.write(response_data.encode('utf-8'))
                    print(f"收到[FindTeamColor]命令，发送响应: {response_data}")
                
                # 处理找球命令
                elif "[FindBall]" in date:
                    # 执行球检测逻辑
                    target_color = team_color  # 首先使用队伍颜色
                    balls = []
                    if frame is not None:
                        balls, mask = detector.detect_color(frame, target_color)
                
                    # 如果没有检测到队伍颜色的球，尝试黑色球
                    if not balls and ELECTRONIC_CONTROL_CONFIG.get("prioritize_black", False):
                        black_balls, black_mask = detector.detect_color(frame, "black")
                        if black_balls:
                            balls = black_balls
                            target_color = "black"
                
                    # 如果还是没有检测到球，尝试黄色球
                    if not balls:
                        yellow_balls, _ = detector.detect_color(frame, "yellow")
                        if yellow_balls:
                            balls = yellow_balls
                            target_color = "yellow"
                
                    if balls:
                        
                        closest_ball = min(balls, key=lambda x: x[2])#找出最近的球
                        cx, cy, distance, _ = closest_ball  # 解包：中心x坐标、中心y坐标、距离（毫米），多加一点忽略像素直径
                        distance_cm = distance / 10.0  # 转换为厘米
                        
                        # 计算角度
                        img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心点x坐标
                        img_center_y = CAMERA_CONFIG["resolution"][1] / 2  # 图像中心点y坐标
                        
                        # 水平角度计算
                        horizontal_offset = cx - img_center_x  # 水平方向偏移
                        fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # 水平视场角，其实默认本身就是60度
                        angle_per_pixel_horizontal = fov_horizontal / CAMERA_CONFIG["resolution"][0]  # 每像素对应的水平角度
                        horizontal_angle = horizontal_offset * angle_per_pixel_horizontal  # 计算水平角度
                        
                        # 垂直角度计算
                        vertical_offset = img_center_y - cy  # 垂直方向偏移（上为正，下为负）
                        fov_vertical = CAMERA_CONFIG.get("vertical_fov", 45)  # 垂直视场角
                        angle_per_pixel_vertical = fov_vertical / CAMERA_CONFIG["resolution"][1]  # 每像素对应的垂直角度
                        vertical_angle = vertical_offset * angle_per_pixel_vertical  # 计算垂直角度
                        
                        ball_info = [int(horizontal_angle), int(vertical_angle), int(distance_cm)]
                
                    # 按照指定格式构建响应数据：[水平角度,垂直角度,距离]
                    response_data = f"[{ball_info[0]},{ball_info[1]},{ball_info[2]}]"
                    ser.write(response_data.encode('utf-8'))
                    print(f"收到[FindBall]命令，发送响应: {response_data}")
                
                elif "[FindPlace]" in date :
                    print("收到[FindPlace]命令,开始检测安全区")
                    if frame is not None:
                        # 调用detect_safe_zone方法检测安全区，并传入队伍颜色参数
                        safe_zone = detector.detect_safe_zone(frame, team_color)
                    
                    if safe_zone is not None:  # 如果检测到安全区
                        x, y, w, h = safe_zone  # 解包安全区的坐标和大小 [x,y,width,height]
                        
                        # 计算安全区中心坐标
                        cx = x + w // 2  # 安全区中心x坐标
                        cy = y + h // 2  # 安全区中心y坐标
                        
                        # 计算角度：基于图像中心点的偏移
                        img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心点x坐标
                        horizontal_offset = cx - img_center_x  # 水平方向偏移量
                        
                        # 角度计算
                        fov_horizontal = 60  # 水平视场角（度）
                        angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]  # 每像素对应的角度
                        safe_zone_angle = horizontal_offset * angle_per_pixel  # 计算安全区相对于中心的角度
                        
                        # 简单估算距离
                        # 核心原理：安全区在图像中的尺寸与距离成反比
                        # 距离越近，在图像中看起来越大；距离越远，在图像中看起来越小
                        safe_zone_area = w * h  # 计算安全区的面积（像素²）
                        
                        # 距离计算参数
                        base_distance = 520.0  # 基础距离（毫米）
                        base_area = 32214  # 基础面积（像素²）
                        
                        # 使用面积的倒数关系估算距离，并转换为厘米
                        # 避免除零错误，使用max确保分母至少为1
                        safe_zone_distance = int((base_area / max(safe_zone_area, 1)) * base_distance / 10)
                        
                        # 打印调试信息
                        print(f"检测到安全区，位置: ({cx}, {cy}), 角度: {safe_zone_angle:.1f}°, 距离: {safe_zone_distance}cm")
                    else:
                        # 如果没有检测到安全区
                        print("未检测到安全区")
                    
                    response_data = f"[{int(safe_zone_angle)},{safe_zone_distance}]"
                    # 发送响应给电控系统
                    ser.write(response_data.encode('utf-8'))
                    print(f"收到[FindPlace]命令，发送响应: {response_data}")
            except Exception as e:
                # 捕获并打印串口通信错误
                print(f"串口通信错误: {e}")
                serial_enabled = False  # 发生错误时禁用串口通信
        
        # 短暂延时，避免CPU占用过高
        time.sleep(0.1)  # 延时100毫秒
        
    
    except Exception as e:
        print(f"主循环发生错误: {e}")
        break

#释放相机
if camera_init_success:
    try:
        import camera_capture
        if hasattr(camera_capture, 'camera') and camera_capture.camera is not None:
            camera_capture.camera.release()
            print("相机资源已释放")
    except Exception as e:
        print(f"释放相机资源时出错: {e}")
print("程序结束")

# 关闭串口连接
if serial_enabled and ser is not None:
    try:
        ser.close()  # 关闭串口
        print("串口已关闭")
    except Exception as e:
        print(f"关闭串口时出错: {e}")
