import cv2
import numpy as np
import sys
sys.path.append('/home/pi/小车/rescue_vision')
from config import CAMERA_CONFIG, OLOR_RANGES as COLOR_RANGES
from camera_capture import init_camera
from object_detection import ObjectDetector

# 创建测试函数
def detect_nearest_ball(frame, detector, team_color):
  
    # 检测目标颜色
    target_color = team_color
    balls, mask = detector.detect_color(frame, target_color)
    
    # 如果没有检测到队伍颜色，尝试其他颜色
    if not balls and mask is not None and cv2.countNonZero(mask) <= 100:
        # 尝试检测黑色球
        black_balls, black_mask = detector.detect_color(frame, "black")
        if black_balls or (black_mask is not None and cv2.countNonZero(black_mask) > 100):
            balls = black_balls
            target_color = "black"
        else:
            # 尝试检测黄色球
            yellow_balls, _ = detector.detect_color(frame, "yellow")
            if yellow_balls:
                balls = yellow_balls
                target_color = "yellow"
    
    # 处理检测结果
    if balls:
        # 通过min函数找出最近的球（距离最小的）
        # 这里使用lambda函数作为排序键，提取每个球元组中距离
        # min函数会返回距离值最小的那个球的完整信息元组
        closest_ball = min(balls, key=lambda x: x[2])
        
        # 解包最近球的信息：中心x坐标、中心y坐标、距离（毫米）
        # 这样可以方便后续单独使用这些值进行计算和显示
        cx, cy, distance = closest_ball
        
        # 将距离转换为厘米显示
        # 因为距离计算结果是以毫米为单位的，除以10转换为厘米便于直观理解
        distance_cm = distance / 10.0
        
        # 计算角度：基于图像中心点的偏移
        # 图像中心点
        # 获取相机配置中的水平分辨率，除以2得到图像水平中心位置（像素坐标）
        img_center_x = CAMERA_CONFIG["resolution"][0] / 2
        
        # 计算水平偏移（像素）
        # 球的中心x坐标减去图像中心点x坐标，得到水平方向上的偏移量
        # 正值表示球在图像中心右侧，负值表示在左侧
        horizontal_offset = cx - img_center_x
        
        # 角度计算（相机视场角为60度）
        # 这里使用预定义的水平视场角来进行像素到角度的转换
        # 60度的水平视场角意味着相机可以覆盖水平方向上60度的范围
        fov_horizontal = 60  # 水平视场角（度）
        
        # 计算每像素对应的角度值（度/像素）
        # 通过将总水平视场角除以图像的水平分辨率，得到每个像素对应的角度
        # 这个转换因子是将像素坐标转换为实际物理角度的关键
        angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]
        
        # 计算偏移角度
        # 将水平像素偏移量乘以每像素对应的角度值
        # 得到球相对于图像中心的实际角度偏移
        # 正值表示需要右转对准目标，负值表示需要左转对准目标
        angle = horizontal_offset * angle_per_pixel
        
        # 限制角度范围在±90度
        # 使用max和min函数确保计算出的角度不会超出实际可能的范围
        # 这样可以防止因异常检测结果导致角度值过大或过小
        angle = max(-90, min(90, angle))
        
        # 在图像上标记球位置、距离和角度
        # 在检测到的球中心绘制一个绿色的实心圆，半径为5像素
        # 这可以在可视化界面上直观地显示球的位置
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        
        # 格式化距离文本，保留一位小数
        distance_text = f"Distance: {distance_cm:.1f}cm"
        
        # 格式化角度文本，保留一位小数
        angle_text = f"Angle: {angle:.1f}°"
        
        # 在球的位置附近显示距离信息
        # 文本位置在球的右侧上方（x+10, y-10），使用绿色字体
        cv2.putText(frame, distance_text, (cx + 10, cy - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 在球的位置附近显示角度信息
        # 文本位置在球的右侧下方（x+10, y+15），使用黄色字体
        cv2.putText(frame, angle_text, (cx + 10, cy + 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # 返回球的信息：角度(°)、距离（厘米）、中心坐标、目标颜色
        
        # 同时返回所有必要信息，以匹配主程序中的解包操作
        return (f"{int(angle)}°", int(distance_cm), cx, cy, target_color), frame
    
    # 如果没有检测到球，返回None
    return None, frame
def test_ball_detection():
    print("开始测试detect_nearest_ball函数...")
    
    # 初始化检测器（不需要实际相机）
    detector = ObjectDetector()
    
    # 创建一个简单的测试图像
    # 黑色背景，中间有一个红色圆形
    width, height = CAMERA_CONFIG["resolution"]
    test_frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 绘制一个红色圆形作为测试目标
    center_x, center_y = width // 2 + 50, height // 2  # 稍微偏右
    radius = 30
    cv2.circle(test_frame, (center_x, center_y), radius, (0, 0, 255), -1)  # BGR格式，红色为(0,0,255)
    
    print(f"创建了测试图像：红色圆位于({center_x}, {center_y})")
    
    # 调用我们的函数
    ball_info, result_frame = detect_nearest_ball(test_frame, detector, "red")
    
    if ball_info:
        angle, distance_cm, cx, cy, color = ball_info
        print(f"测试成功！检测到球：")
        print(f"  角度: {angle}度")
        print(f"  距离: {distance_cm}厘米")
        print(f"  中心坐标: ({cx}, {cy})")
        print(f"  颜色: {color}")
        
        # 保存结果图像以便检查
        cv2.imwrite("test_result.jpg", result_frame)
        print("测试结果图像已保存为'test_result.jpg'")
    else:
        print("测试失败：未检测到球")
        
    print("测试完成。")

if __name__ == "__main__":
    test_ball_detection()
