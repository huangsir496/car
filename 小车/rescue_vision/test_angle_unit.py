import cv2
import numpy as np
from main import detect_nearest_ball
from object_detection import ObjectDetector

# 创建测试图像
height, width = 480, 640
frame = np.zeros((height, width, 3), dtype=np.uint8)

# 在图像中心偏右位置绘制一个红色圆形作为测试目标
center_x, center_y = 370, 240  # 图像中心偏右位置
radius = 20
cv2.circle(frame, (center_x, center_y), radius, (0, 0, 255), -1)  # BGR格式，红色为(0,0,255)

# 初始化检测器
team_color = "red"
detector = ObjectDetector()

# 测试detect_nearest_ball函数
ball_info, result_frame = detect_nearest_ball(frame, detector, team_color)

# 打印结果
if ball_info:
    angle_with_unit, distance_cm, cx, cy, target_color = ball_info
    print(f"检测结果：")
    print(f"角度: {angle_with_unit} (应包含单位°)")
    print(f"距离: {distance_cm}cm")
    print(f"中心坐标: ({cx}, {cy})")
    print(f"目标颜色: {target_color}")
    
    # 保存测试结果图像
    cv2.imwrite("test_angle_unit_result.jpg", result_frame)
    print("测试结果图像已保存为 test_angle_unit_result.jpg")
    
    # 验证角度带单位
    if isinstance(angle_with_unit, str) and angle_with_unit.endswith('°'):
        print("✓ 角度带单位功能正常工作")
        
        # 测试角度值提取
        try:
            # 移除单位后尝试转换为整数
            angle_value = int(angle_with_unit.rstrip('°'))
            print(f"✓ 成功从带单位的角度中提取数值: {angle_value}")
        except ValueError:
            print("✗ 无法从带单位的角度中提取数值")
    else:
        print("✗ 角度未正确添加单位")
else:
    print("✗ 未能检测到球")

print("\n测试完成！")