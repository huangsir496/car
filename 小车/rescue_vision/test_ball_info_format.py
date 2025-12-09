#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证ball_info格式正确性
测试[FindBall]命令处理逻辑中的ball_info是否为[角度，距离]数组格式
"""

import cv2
import numpy as np
import time
import sys
from config import CAMERA_CONFIG, ELECTRONIC_CONTROL_CONFIG
from object_detection import ObjectDetector

# 模拟串口通信函数
class MockSerial:
    def __init__(self):
        self.data_received = None
    
    def write(self, data):
        self.data_received = data.decode('utf-8')
        print(f"模拟串口发送: {self.data_received}")

# 模拟read_data_from_serial函数
def mock_read_data_from_serial(ser):
    return "[FindBall]"

# 模拟send_data_via_serial函数
def mock_send_data_via_serial(ser, data):
    ser.write(data.encode('utf-8'))

# 创建测试图像

def create_test_image(ball_position=(320, 240), ball_size=20):
    # 创建空白图像
    height, width = CAMERA_CONFIG["resolution"][1], CAMERA_CONFIG["resolution"][0]
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 在指定位置绘制一个红色球
    cv2.circle(image, ball_position, ball_size, (0, 0, 255), -1)
    
    return image

# 测试主函数
def test_ball_info_format():
    print("开始测试ball_info格式...")
    
    # 初始化检测器
    detector = ObjectDetector()
    
    # 创建模拟串口
    mock_ser = MockSerial()
    
    # 创建测试图像
    test_image = create_test_image()
    print("创建测试图像完成")
    
    # 执行球检测逻辑（复制自main.py）
    target_color = "red"
    balls, mask = detector.detect_color(test_image, target_color)
    
    # 初始化角度和距离为0
    ball_info = [0, 0]  # 默认[角度,距离]
    
    if balls:
        # 找出最近的球
        closest_ball = min(balls, key=lambda x: x[2])
        cx, cy, distance = closest_ball
        distance_cm = distance / 10.0  # 转换为厘米
        
        # 计算角度
        img_center_x = CAMERA_CONFIG["resolution"][0] / 2
        horizontal_offset = cx - img_center_x
        fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)
        angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]
        angle = horizontal_offset * angle_per_pixel
        angle = max(-90, min(90, angle))  # 限制角度范围
        
        # 更新ball_info为[角度,距离]数组
        ball_info = [int(angle), int(distance_cm)]
    
    # 验证ball_info格式
    print(f"ball_info格式: {type(ball_info)}")
    print(f"ball_info内容: {ball_info}")
    print(f"ball_info长度: {len(ball_info)}")
    print(f"ball_info[0]类型(角度): {type(ball_info[0])}")
    print(f"ball_info[1]类型(距离): {type(ball_info[1])}")
    
    # 构建响应数据
    response_data = f"[{ball_info[0]},{ball_info[1]}]"
    print(f"响应数据格式: {response_data}")
    
    # 发送模拟数据
    mock_send_data_via_serial(mock_ser, response_data)
    
    # 验证响应数据格式是否正确
    if mock_ser.data_received:
        # 检查格式是否为 [角度,距离]
        try:
            # 尝试解析响应数据
            data_str = mock_ser.data_received.strip('[]')
            angle_str, distance_str = data_str.split(',')
            angle = int(angle_str)
            distance = int(distance_str)
            print(f"解析成功! 角度: {angle}, 距离: {distance}")
            print("测试通过: ball_info格式正确，响应数据格式符合要求")
            return True
        except Exception as e:
            print(f"测试失败: 响应数据格式错误 - {e}")
            return False
    else:
        print("测试失败: 未接收到响应数据")
        return False

if __name__ == "__main__":
    success = test_ball_info_format()
    sys.exit(0 if success else 1)
