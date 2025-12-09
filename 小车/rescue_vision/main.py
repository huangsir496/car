# cv2: OpenCV库，用于图像处理和计算机视觉
import cv2
# numpy: 数值计算库，用于数组操作
import numpy as np
# time: 时间处理库，用于延时和计时
import time
# math: 数学函数库，用于数学计算
import math
# serial: 串口通信库，用于与电控系统通信
import serial

# 从配置文件导入配置参数
from config import (
    CAMERA_CONFIG,       # 相机参数配置
    VISION_CONFIG,       # 视觉处理配置
    COLOR_RANGES,        # 颜色HSV阈值范围配置
    ELECTRONIC_CONTROL_CONFIG  # 电控系统通信配置
)

# 导入自定义模块
from camera_capture import init_camera, get_frame # 相机捕获模块
from object_detection import ObjectDetector  # 目标检测模块


# 配置队伍颜色

team_color = "red"

# 初始化相机和检测器
# 初始化相机


# 初始化相机
camera_init_success = init_camera()
if not camera_init_success:
    print("相机初始化失败，但程序将继续运行串口通信部分")
    # 不退出程序，允许继续运行串口通信
# 创建目标检测器对象，用于识别球体和安全区域
detector = ObjectDetector()

# 初始化串口通信
# 串口用于与电控系统进行数据交换
try:
    # 从配置中获取串口参数
    serial_port = "/dev/ttyS0" # 串口设备路径
    baud_rate = 9600      # 波特率
    
    # 打开串口
    ser = serial.Serial(serial_port, baud_rate, timeout=0.1)  # 减小超时时间以提高响应速度
    
    # 检查串口是否成功打开
    if ser.is_open:
        print(f"串口 {serial_port} 已成功打开")
        serial_enabled = True  # 标记串口可用
    else:
        print(f"串口 {serial_port} 已创建但未打开")
        serial_enabled = False

except Exception as e:
    # 处理串口打开失败的情况
    print(f"无法打开串口: {e}")
    ser = None
    serial_enabled = False



# 主程序逻辑
# 这是Python的标准写法，当该脚本被直接运行时才执行以下代码
if __name__ == "__main__":
    # 主循环：不断处理视频帧和串口命令
    while True:
        try:
            # 从相机获取一帧图像
            frame = get_frame()

            
            # 如果无法获取图像，短暂暂停后继续
            if frame is None:
                print("无法获取图像帧，继续尝试...")
                time.sleep(0.01)  # 短暂睡眠避免CPU占用过高
                continue
            
            # 主循环其他处理逻辑将在后续的串口命令处理中进行
        except Exception as e:
            print(f"主循环处理错误: {e}")
            time.sleep(0.01)
        
        
        
        # 显示结果图像
        # 创建一个名为'Ball Detection'的窗口并显示当前处理的帧
        # cv2.imshow('Ball Detection', frame)  # 注释掉这行代码，避免缺少图形界面支持的错误
        
        # 第二处串口命令处理（这部分包含了所有命令的处理逻辑）
        if serial_enabled and ser is not None:
            try:
                # 读取串口消息
                if ser.in_waiting > 0:  # 检测是否有数据待读取
                    data = ser.read_all().decode('utf-8', errors='ignore')
                    if data:
                        print(f"收到电控数据：{data.strip()}")  # 打印收到的原始数据
                        if "[FindTeamColor]" in data:
                            target_color = team_color  # 首先使用队伍颜色
                            balls = []
                            ball_info = [0, 0]  # 默认[角度,距离]
                            if frame is not None:
                                balls, mask = detector.detect_color(frame, target_color)
                            
                            if balls:
                                # 找出最近的球（根据距离排序）
                                closest_ball = min(balls, key=lambda x: x[2])
                                cx, cy, distance = closest_ball  # 解包：中心x坐标、中心y坐标、距离（毫米）
                                distance_cm = distance / 10.0  # 转换为厘米
                                
                                # 计算角度
                                img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心点x坐标
                                horizontal_offset = cx - img_center_x  # 水平方向偏移
                                fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # 水平视场角
                                angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]  # 每像素对应的角度
                                angle = horizontal_offset * angle_per_pixel  # 计算角度
                                
                                ball_info = [int(angle), int(distance_cm)]
                            
                            # 按照指定格式构建响应数据：[角度,距离]
                            response_data = f"[{ball_info[0]},{ball_info[1]}]"
                            ser.write(response_data.encode('utf-8'))
                            print(f"收到[FindTeamColor]命令，发送响应: {response_data}")
                        # 处理找球命令
                        elif "[FindBall]" in data:
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
                            
                            # 初始化角度和距离为0
                            ball_info = [0, 0]  # 默认[角度,距离]
                            
                            if balls:
                                # 找出最近的球（根据距离排序）
                                closest_ball = min(balls, key=lambda x: x[2])
                                cx, cy, distance = closest_ball  # 解包：中心x坐标、中心y坐标、距离（毫米）
                                distance_cm = distance / 10.0  # 转换为厘米
                                
                                # 计算角度
                                img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心点x坐标
                                horizontal_offset = cx - img_center_x  # 水平方向偏移
                                fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # 水平视场角
                                angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]  # 每像素对应的角度
                                angle = horizontal_offset * angle_per_pixel  # 计算角度
                                
                                ball_info = [int(angle), int(distance_cm)]
                            
                            # 按照指定格式构建响应数据：[角度,距离]
                            response_data = f"[{ball_info[0]},{ball_info[1]}]"
                            ser.write(response_data.encode('utf-8'))
                            print(f"收到[FindBall]命令，发送响应: {response_data}")
                        # 处理检查球是否被套住的命令
                        elif "[CheakBall]" in data:
                            # 检测小球是否被套住的功能
                            # 核心思想：在套子区域内同时检测到套子颜色和球的颜色，则认为球被套住
                            is_ball_caught = False  # 初始化球被套住状态为False
                            
                            # 定义套子区域 - 这是一个关键参数，决定了检查的区域范围
                            # 使用当前已获取的frame图像，避免重复读取相机
                            if frame is not None:
                                h, w = frame.shape[:2]  # 获取图像的高度和宽度
                                
                                # 定义套子区域：取图像中心的1/3区域
                                crop_x = w // 3  # 裁剪区域的起始x坐标
                                crop_y = h // 3  # 裁剪区域的起始y坐标
                                crop_w = w // 3  # 裁剪区域的宽度
                                crop_h = h // 3  # 裁剪区域的高度
                        
                                # 截取套子区域图像
                                # OpenCV的图像坐标系是[y,x]，与数学坐标系相反
                                cropped_image = frame[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
                                
                                # 在套子区域内检测各种颜色
                                detected_colors = {}  # 存储各种颜色的检测结果
                                
                                # 检测红色
                                red_balls, red_mask = detector.detect_color(cropped_image, "red")
                                # 如果检测到红色球或者红色像素超过阈值50，则认为检测到红色
                                detected_colors["red"] = red_balls or (red_mask is not None and cv2.countNonZero(red_mask) > 50)

                                # 检测蓝色
                                blue_balls, blue_mask = detector.detect_color(cropped_image, "blue")
                                detected_colors["blue"] = blue_balls or (blue_mask is not None and cv2.countNonZero(blue_mask) > 50)
                                
                                # 检测黑色
                                black_balls, black_mask = detector.detect_color(cropped_image, "black")
                                detected_colors["black"] = black_balls or (black_mask is not None and cv2.countNonZero(black_mask) > 50)
                                
                                # 检测黄色
                                yellow_balls, yellow_mask = detector.detect_color(cropped_image, "yellow")
                                detected_colors["yellow"] = yellow_balls or (yellow_mask is not None and cv2.countNonZero(yellow_mask) > 50)
                                
                                # 检测白色（套子的颜色）
                                white_balls, white_mask = detector.detect_color(cropped_image, "white")
                                detected_colors["white"] = white_balls or (white_mask is not None and cv2.countNonZero(white_mask) > 50)
                                
                                # 计算检测到的颜色数量
                                detected_color_count = 0
                                for color, detected in detected_colors.items():
                                    if detected:  # 如果该颜色被检测到
                                        detected_color_count += 1
                                
                                color_content = []  # 存储检测到的颜色列表

                                # 判断逻辑：
                                # 1. 如果检测到白色（套子）和另一种颜色（球），则认为被套住
                                # 2. 排除特定的黄色组合情况
                                has_sleeve = detected_colors["white"]  # 是否检测到套子（白色）
                                has_target_ball = detected_colors[team_color] or detected_colors["black"]  # 是否检测到目标球
                                has_yellow = detected_colors["yellow"]  # 是否检测到黄色
                                
                                # 只有检测到至少两种颜色时才进行判断
                                if detected_color_count >= 2:
                                    # 检查特定的颜色组合
                                    if has_sleeve and has_yellow and detected_color_count >= 3:
                                        is_ball_caught = False  # 套子+黄色+其他颜色：排除
                                        print("检测到黄色+*组合，排除")
                                    elif has_sleeve and has_yellow and detected_color_count == 2:
                                        is_ball_caught = True  # 套子+黄色：认为被套住
                                        print("黄色")
                                    elif has_sleeve and has_target_ball:
                                        is_ball_caught = True  # 套子+目标球：认为被套住
                                        # 记录检测到的颜色组合
                                        for color, detected in detected_colors.items():
                                            if detected:
                                                color_content.append(color)
                                        print(f"检测到被套住的组合: {color_content}")
                                    else:
                                        is_ball_caught = False  # 其他组合：排除
                                        print("检测到其他组合，排除")
                            
                            # 根据检测结果构建响应
                            if is_ball_caught:
                                response_data = "[OK]"  # 球被套住的响应
                                print("收到[CheakBall]命令，检测结果：球被套住")
                            else:
                                response_data = "[NO]"  # 球未被套住的响应
                                print("收到[CheakBall]命令，检测结果：球未被套住")
                            
                            # 发送响应数据给电控系统
                            ser.write(response_data.encode('utf-8'))
                        # 处理寻找安全区的命令
                        elif "[FindPlace]" in data:   
                            # 检测队伍颜色的安全区位置
                            # 安全区通常是与队伍颜色相同的目标区域
                            safe_zone_angle = 0  # 初始化安全区角度为0
                            safe_zone_distance = 0  # 初始化安全区距离为0
                            
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
                                    
                                    # 在图像上标记安全区位置
                                    # 使用紫红色矩形框(255,0,255)，线宽为2
                                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
                                    # 在矩形框上方添加"Safe Zone"文字标签
                                    cv2.putText(frame, "Safe Zone", (x, y - 10), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                                    
                                    # 打印调试信息
                                    print(f"检测到安全区，位置: ({cx}, {cy}), 角度: {safe_zone_angle:.1f}°, 距离: {safe_zone_distance}cm")
                                else:
                                    # 如果没有检测到安全区
                                    print("未检测到安全区")
                            
                            # 构建响应数据，格式为[角度,距离]
                            response_data = f"[{int(safe_zone_angle)},{safe_zone_distance}]"
                            
                            # 发送响应给电控系统
                            ser.write(response_data.encode('utf-8'))
                            print(f"收到[FindPlace]命令，发送响应: {response_data}")
                        # 如果没有识别到特定命令，发送默认响应（类似text.py的行为）
                        else:
                            # 发送默认响应，确保电控能收到回复
                            default_response = "[0,0]"
                            ser.write(default_response.encode('utf-8'))
                            print(f"未识别命令，发送默认响应: {default_response}")
            except Exception as e:
                # 捕获并打印串口通信错误
                print(f"串口通信错误: {e}")
                serial_enabled = False  # 发生错误时禁用串口通信
        
        # 检查退出按键 - 注释掉图形界面相关代码
        # key = cv2.waitKey(1) & 0xFF  # 等待1毫秒并获取按键
        # if key == 27:  # 按下ESC键（ASCII码27）
        #     print("退出检测")
        #     break  # 退出主循环
        # 添加一个简单的条件来定期检查是否需要退出（例如运行一段时间后自动退出）
        time.sleep(0.1)  # 增加一点延时，减少CPU占用
        
        # 短暂延时，避免CPU占用过高
        time.sleep(0.01)  # 延时10毫秒
    
# 程序结束时的资源释放
# 关闭所有OpenCV创建的窗口 - 注释掉图形界面相关代码
# cv2.destroyAllWindows()


print("程序结束")

# 关闭串口连接（如果启用了串口）
if serial_enabled and ser is not None:
    try:
        ser.close()  # 关闭串口
        print("串口已关闭")
    except:  # 捕获可能的异常
        pass  # 静默处理异常