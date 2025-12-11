import cv2
import numpy as np
from config import CAMERA_CONFIG, SAFE_ZONE_CONFIG
from object_detection import ObjectDetector

class SafeZoneTester:
    def __init__(self):
        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)  # 0表示默认摄像头
        self.cap.set(3, CAMERA_CONFIG["resolution"][0])
        self.cap.set(4, CAMERA_CONFIG["resolution"][1])
        
        # 创建物体检测器
        self.detector = ObjectDetector()
        
        # 配置参数
        self.fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # 水平视场角
        self.img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # 图像中心x坐标
        self.img_center_y = CAMERA_CONFIG["resolution"][1] / 2  # 图像中心y坐标
        
        # 安全区距离计算参数
        self.base_distance = SAFE_ZONE_CONFIG["base_distance"]  # 基础距离（毫米）
        self.base_area = SAFE_ZONE_CONFIG["base_area"]  # 基础面积（像素²）
        
        print("安全区检测测试程序已启动")
        print("按'q'键退出")
        print("按'd'键切换调试信息")
    
    def calibrate(self, detected_area):
        """校准安全区距离计算参数"""
        if detected_area <= 0:
            print("无法校准：未检测到安全区")
            return
        
        try:
            # 获取用户输入的实际距离（厘米）
            actual_distance_cm = float(input("请输入安全区的实际距离（厘米）: "))
            actual_distance_mm = actual_distance_cm * 10  # 转换为毫米
            
            # 根据实际距离和检测面积计算新的基础面积
            # 公式：base_area = (detected_area * base_distance) / actual_distance_mm
            new_base_area = int((detected_area * self.base_distance) / actual_distance_mm)
            
            print(f"校准结果：")
            print(f"  检测面积: {detected_area} px²")
            print(f"  实际距离: {actual_distance_cm} cm")
            print(f"  当前基础面积: {self.base_area} px²")
            print(f"  当前基础距离: {self.base_distance} mm")
            print(f"  新基础面积: {new_base_area} px²")
            
            # 更新基础面积
            self.base_area = new_base_area
            print("校准完成！基础面积已更新")
            
        except ValueError:
            print("输入错误：请输入有效的数字")
            return
    
    def run(self):
        show_debug = False  # 控制是否显示调试信息
        detected_area = 0  # 存储最后一次检测到的安全区面积
        
        while True:
            # 读取摄像头帧
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read camera frame")
                break
            
            # 检测安全区
            safe_zone, contour_area = self.detector.detect_safe_zone(frame)
            detected_area = contour_area  # 更新检测面积
            
            # 在图像上绘制结果
            result_frame = frame.copy()
            
            if safe_zone is not None:
                x, y, w, h = safe_zone
                # 绘制安全区边界框
                cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 计算安全区中心
                cx = x + w // 2
                cy = y + h // 2
                # 绘制中心标记
                cv2.circle(result_frame, (cx, cy), 5, (0, 255, 0), -1)
                # 显示安全区信息
                cv2.putText(result_frame, "safe zone", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # 计算安全区角度
                horizontal_offset = cx - self.img_center_x
                angle_per_pixel = self.fov_horizontal / CAMERA_CONFIG["resolution"][0]
                safe_zone_angle = horizontal_offset * angle_per_pixel
                
                # 计算安全区距离
                safe_zone_area = contour_area  # 使用实际轮廓面积
                # 显示面积信息
                area_text = f"轮廓面积: {safe_zone_area}px²"
                cv2.putText(result_frame, area_text, (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                
                # 计算距离的中间过程
                ratio = self.base_area / max(safe_zone_area, 1)
                distance_mm = ratio * self.base_distance
                safe_zone_distance = int(distance_mm / 10)  # 转换为厘米
                
                # 显示角度和距离信息
                safe_zone_text = f"angle: {safe_zone_angle:.1f}° distance: {safe_zone_distance}cm"
                cv2.putText(result_frame, safe_zone_text, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                if show_debug:
                    # 显示安全区尺寸信息
                    size_text = f"W: {w}px, H: {h}px"
                    cv2.putText(result_frame, size_text, (x, y + h + 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # 显示中心坐标
                    center_text = f"中心: ({cx}, {cy})"
                    cv2.putText(result_frame, center_text, (10, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # 显示距离计算调试信息
                    debug_text = f"基础面积: {self.base_area}px² 基础距离: {self.base_distance}mm 比例: {ratio:.2f} 距离(mm): {distance_mm:.1f}"
                    cv2.putText(result_frame, debug_text, (10, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            else:
                # 未检测到安全区
                cv2.putText(result_frame, "No safe zone detected", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # 显示操作提示
            cv2.putText(result_frame, "Press 'd' to toggle debug", (10, result_frame.shape[0] - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(result_frame, "Press 'c' to calibrate", (10, result_frame.shape[0] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # 显示结果窗口
            cv2.imshow("Safe Zone Detection - Press q to quit", result_frame)
            
            # 处理键盘输入
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                show_debug = not show_debug
                print(f"Debug info {'enabled' if show_debug else 'disabled'}")
            elif key == ord('c'):
                print("开始校准...")
                self.calibrate(detected_area)
        
        # 释放资源
        self.cap.release()
        cv2.destroyAllWindows()
        print("Program exited")

if __name__ == "__main__":
    tester = SafeZoneTester()
    tester.run()
