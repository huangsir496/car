import cv2
import numpy as np
import math
from config import CAMERA_CONFIG, COLOR_RANGES, TARGET_CONFIG, VISION_CONFIG, SAFE_ZONE_CONFIG
from object_detection import ObjectDetector

class BallDetectionTester:
    def __init__(self):
        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)  # 0表示默认摄像头
        self.cap.set(3, CAMERA_CONFIG["resolution"][0])
        self.cap.set(4, CAMERA_CONFIG["resolution"][1])
        
        # 创建物体检测器
        self.detector = ObjectDetector()
        
        # 配置参数
        self.team_color = "red"  # 可以更改为"blue"或其他颜色
        self.fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # 水平视场角
        self.fov_vertical = CAMERA_CONFIG.get("vertical_fov", 45)  # 垂直视场角
        self.img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心x坐标
        self.img_center_y = CAMERA_CONFIG["resolution"][1] / 2  # 图像中心y坐标
        
        # 距离计算参数
        self.pixel_distance_scale = VISION_CONFIG.get("ball_distance_scale", 15000)
        self.pixel_distance_offset = VISION_CONFIG.get("ball_distance_offset", 0)
        
        print("小球检测测试程序已启动")
        print("按'q'键退出")
        print("按'r'键切换到红色小球检测")
        print("按'b'键切换到蓝色小球检测")
        print("按'k'键切换到黑色小球检测")
        print("按'y'键切换到黄色小球检测")
    
    def calculate_angle(self, cx, cy):
        """计算相对于图像中心的水平和垂直角度"""
        # 水平角度计算
        horizontal_offset = cx - self.img_center_x
        angle_per_pixel_horizontal = self.fov_horizontal / CAMERA_CONFIG["resolution"][0]
        horizontal_angle = horizontal_offset * angle_per_pixel_horizontal
        
        # 垂直角度计算
        vertical_offset = self.img_center_y - cy  # 上为正，下为负
        angle_per_pixel_vertical = self.fov_vertical / CAMERA_CONFIG["resolution"][1]
        vertical_angle = vertical_offset * angle_per_pixel_vertical
        
        return horizontal_angle, vertical_angle
    
    def run(self):
        show_vertical_angle = False  # 控制是否显示垂直角度
        show_safe_zone = False  # 控制是否显示安全区
        
        print("按'p'键切换安全区检测")
        
        while True:
            # 读取摄像头帧
            ret, frame = self.cap.read()
            if not ret:
                print("读取摄像头帧失败")
                break
            
            # 检测小球
            balls, mask = self.detector.detect_color(frame, self.team_color)
            
            # 检测安全区
            safe_zone, contour_area = self.detector.detect_safe_zone(frame, self.team_color)
            safe_zone_angle = 0
            safe_zone_distance = 0
            
            # 处理检测结果
            if balls:
                # 找到最近的小球
                closest_ball = balls[0]  # balls已经按距离排序
                cx, cy, distance = closest_ball
                
                # 计算角度
                horizontal_angle, vertical_angle = self.calculate_angle(cx, cy)
                
                # 转换单位
                distance_cm = distance / 10.0
                
                # 在图像上绘制结果
                # 绘制小球中心
                cv2.circle(frame, (int(cx), int(cy)), 5, (0, 255, 0), -1)  # 中心点
                
                # 根据距离计算小球的像素直径（距离与像素大小成反比）
                distance_adjusted = distance - self.pixel_distance_offset
                if distance_adjusted <= 0:
                    distance_adjusted = 1  # 避免除以零
                ball_diameter_pixels = int(self.pixel_distance_scale / distance_adjusted)
                if ball_diameter_pixels < 5:
                    ball_diameter_pixels = 5
                
                # 绘制小球边界框
                half_diameter = ball_diameter_pixels // 2
                x = int(cx - half_diameter)
                y = int(cy - half_diameter)
                w = h = ball_diameter_pixels
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # 黄色边界框
                
                # 显示距离和角度信息
                if show_vertical_angle:
                    info_text = f"颜色: {self.team_color} 距离: {distance_cm:.1f}cm 水平角度: {horizontal_angle:.1f}° 垂直角度: {vertical_angle:.1f}°"
                else:
                    info_text = f"颜色: {self.team_color} 距离: {distance_cm:.1f}cm 角度: {horizontal_angle:.1f}°"
                cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # 绘制图像中心线
                cv2.line(frame, (int(self.img_center_x), 0), (int(self.img_center_x), frame.shape[0]), (0, 255, 255), 2)
                cv2.line(frame, (0, int(self.img_center_y)), (frame.shape[1], int(self.img_center_y)), (0, 255, 255), 2)
                
                # 绘制从中心到小球的连线
                cv2.line(frame, (int(self.img_center_x), int(self.img_center_y)), (int(cx), int(cy)), (255, 0, 0), 2)
                
                # 显示小球的像素直径
                ball_diameter_pixels = max(w, h)
                diameter_text = f"直径: {ball_diameter_pixels}px"
                cv2.putText(frame, diameter_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            else:
                # 未检测到小球
                cv2.putText(frame, f"未检测到{self.team_color}小球", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # 处理安全区检测结果
            if show_safe_zone and safe_zone is not None:
                x, y, w, h = safe_zone  # 解包安全区的坐标和大小 [x,y,width,height]
                
                # 绘制安全区边界框
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # 计算安全区中心坐标
                cx = x + w // 2  # 安全区中心x坐标
                cy = y + h // 2  # 安全区中心y坐标
                
                # 绘制安全区中心标记
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                
                # 计算安全区角度
                horizontal_offset = cx - self.img_center_x  # 水平方向偏移量
                angle_per_pixel = self.fov_horizontal / CAMERA_CONFIG["resolution"][0]  # 每像素对应的角度
                safe_zone_angle = horizontal_offset * angle_per_pixel  # 计算安全区相对于中心的角度
                
                # 计算安全区距离（与main.py保持一致的方法）
                safe_zone_area = contour_area  # 使用实际轮廓面积
                
                # 从配置文件获取距离计算参数
                base_distance = SAFE_ZONE_CONFIG["base_distance"]  # 基础距离（毫米）
                base_area = SAFE_ZONE_CONFIG["base_area"]  # 基础面积（像素²）
                
                # 使用面积的倒数关系估算距离，并转换为厘米
                # 避免除零错误，使用max确保分母至少为1
                safe_zone_distance = int((base_area / max(safe_zone_area, 1)) * base_distance / 10)
                
                # 显示安全区信息
                cv2.putText(frame, "安全区", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                safe_zone_text = f"角度: {safe_zone_angle:.1f}° 距离: {safe_zone_distance}cm"
                cv2.putText(frame, safe_zone_text, (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 显示掩码图像（可选）
            mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # 合并原始图像和掩码图像用于显示
            combined = np.hstack((frame, mask_rgb))
            
            # 显示窗口
            cv2.imshow("小球检测测试 - 按q键退出", combined)
            
            # 处理键盘输入
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.team_color = "red"
                print("已切换到红色小球检测")
            elif key == ord('b'):
                self.team_color = "blue"
                print("已切换到蓝色小球检测")
            elif key == ord('k'):
                self.team_color = "black"
                print("已切换到黑色小球检测")
            elif key == ord('y'):
                self.team_color = "yellow"
                print("已切换到黄色小球检测")
            elif key == ord('p'):
                show_safe_zone = not show_safe_zone
                print(f"安全区检测{'已开启' if show_safe_zone else '已关闭'}")
            elif key == ord('v'):
                show_vertical_angle = not show_vertical_angle
                print(f"垂直角度显示{'已开启' if show_vertical_angle else '已关闭'}")
        
        # 释放资源
        self.cap.release()
        cv2.destroyAllWindows()
        print("程序已退出")

if __name__ == "__main__":
    tester = BallDetectionTester()
    tester.run()