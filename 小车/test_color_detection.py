#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
颜色检测测试脚本
用于验证目标检测功能是否正常工作
"""

import cv2
import numpy as np
import time
import sys
import os

# 添加rescue_vision目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'rescue_vision'))

from config import COLOR_RANGES, CAMERA_CONFIG, VISION_CONFIG, TARGET_CONFIG
from object_detection import ObjectDetector
from camera_capture import init_camera, get_frame

def test_color_detection():
    """测试颜色检测功能"""
    print("=== 颜色检测测试 ===")
    
    # 初始化相机
    print("正在初始化相机...")
    camera_init_success = init_camera()
    if not camera_init_success:
        print("相机初始化失败！")
        return False
    
    # 初始化检测器
    print("正在初始化检测器...")
    detector = ObjectDetector()
    
    # 测试的颜色列表
    test_colors = ["red", "blue", "black", "yellow"]
    team_color = "red"  # 测试队伍颜色
    
    print(f"\n当前队伍颜色: {team_color}")
    print(f"测试颜色: {test_colors}")
    print("\n按 'q' 退出测试")
    
    # 循环测试
    while True:
        # 获取图像
        frame = get_frame()
        if frame is None:
            print("无法获取图像帧，继续尝试...")
            time.sleep(0.01)
            continue
        
        # 复制原始图像用于显示
        display_frame = frame.copy()
        
        # 测试所有颜色
        for color in test_colors:
            balls, mask = detector.detect_color(frame, color)
            
            # 如果检测到球，标记它们
            if balls:
                print(f"检测到 {len(balls)} 个{color}球")
                for ball in balls:
                    cx, cy, distance = ball
                    distance_cm = distance / 10.0
                    
                    # 计算角度
                    img_center_x = CAMERA_CONFIG["resolution"][0] / 2
                    horizontal_offset = cx - img_center_x
                    fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)
                    angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]
                    angle = horizontal_offset * angle_per_pixel
                    
                    # 在图像上标记
                    cv2.circle(display_frame, (int(cx), int(cy)), 10, (0, 255, 0), 2)
                    cv2.putText(display_frame, f"{color} {int(angle)}° {int(distance_cm)}cm", 
                                (int(cx) + 15, int(cy) - 15), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    print(f"  - {color}球: 中心({int(cx)}, {int(cy)}), 角度{angle:.1f}°, 距离{distance_cm:.1f}cm")
            else:
                print(f"未检测到{color}球")
        
        # 特别测试FindTeamColor功能
        print(f"\n=== 测试[FindTeamColor]命令 ===")
        target_color = team_color
        balls, mask = detector.detect_color(frame, target_color)
        
        ball_info = [0, 0]
        if balls:
            closest_ball = min(balls, key=lambda x: x[2])
            cx, cy, distance = closest_ball
            distance_cm = distance / 10.0
            
            # 计算角度
            img_center_x = CAMERA_CONFIG["resolution"][0] / 2
            horizontal_offset = cx - img_center_x
            fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)
            angle_per_pixel = fov_horizontal / CAMERA_CONFIG["resolution"][0]
            angle = horizontal_offset * angle_per_pixel
            
            ball_info = [int(angle), int(distance_cm)]
            
            print(f"[FindTeamColor]命令会发送: [{ball_info[0]},{ball_info[1]}]")
        else:
            print(f"[FindTeamColor]命令会发送: [{ball_info[0]},{ball_info[1]}] (未检测到球)")
        
        # 显示处理后的图像
        # 注意：如果在无图形界面的环境中运行，需要注释掉显示部分
        # cv2.imshow("Color Detection Test", display_frame)
        
        # 保存图像到文件，方便查看
        cv2.imwrite("/home/pi/小车/color_detection_test.jpg", display_frame)
        print("\n图像已保存到 /home/pi/小车/color_detection_test.jpg")
        
        # 检查按键
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        # 测试一次就退出
        break
    
    # 清理
    # cv2.destroyAllWindows()
    print("\n=== 测试结束 ===")
    return True

if __name__ == "__main__":
    test_color_detection()
