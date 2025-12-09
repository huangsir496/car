import cv2
import numpy as np
from config import COLOR_RANGES, TARGET_CONFIG, VISION_CONFIG

class ObjectDetector:
    def __init__(self):
        # 从配置文件加载颜色范围
        self.color_ranges = COLOR_RANGES
        
        # 基本目标参数
        self.min_contour_area = TARGET_CONFIG.get("min_contour_area", 20)  # 最小轮廓面积
        self.circularity_threshold = TARGET_CONFIG.get("circularity_threshold", 0.7)  # 圆形度阈值
        
        # 像素-距离转换参数
        self.pixel_distance_scale = 15000  # 缩放因子
        self.pixel_distance_offset = 0  # 偏移量
        
        # 高斯滤波参数 - 保留此功能
        self.gaussian_blur_ksize = VISION_CONFIG.get("gaussian_blur_ksize", (5, 5))
        self.gaussian_blur_sigma = VISION_CONFIG.get("gaussian_blur_sigma", 1)
        
        # 简化的形态学处理参数
        self.kernel = np.ones((3, 3), np.uint8)

    def calculate_distance(self, ball_diameter_pixels):
        """根据球体在图像中的直径计算实际距离
        
        Args:
            ball_diameter_pixels: 球体在图像中的直径（像素）
            
        Returns:
            distance: 球体与相机的距离（mm）
        """
        if ball_diameter_pixels <= 5:  # 过滤过小的检测结果
            return float('inf')
        
        # 使用像素-距离的反比关系计算距离
        distance = (self.pixel_distance_scale / ball_diameter_pixels) + self.pixel_distance_offset
        
        # 限制距离范围
        if distance   > 5000:  # 限制到5m范围内
            return float('inf')
            
        return distance
    
    def detect_color(self, frame, color):
        """根据颜色检测目标"""
        print(f"调试: 检测{color}颜色")
        # 直接使用原图
        processed_frame = frame
        
        # 应用高斯滤波减少噪声
        blurred_frame = cv2.GaussianBlur(processed_frame, self.gaussian_blur_ksize, self.gaussian_blur_sigma)
        
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        
        # 根据颜色获取对应的HSV范围并创建掩码
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        if color in self.color_ranges:
            color_data = self.color_ranges[color]
            
            if color == 'red':
                # 红色需要特殊处理，使用两个范围
                if len(color_data) == 4:
                    # 格式: [lower1, upper1, lower2, upper2]
                    lower1, upper1, lower2, upper2 = color_data
                    mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
                    mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
                    mask = cv2.bitwise_or(mask1, mask2)
                elif len(color_data) == 12:
                    # 格式: [H1_min, S1_min, V1_min, H1_max, S1_max, V1_max, H2_min, S2_min, V2_min, H2_max, S2_max, V2_max]
                    lower1 = np.array(color_data[:3])
                    upper1 = np.array(color_data[3:6])
                    lower2 = np.array(color_data[6:9])
                    upper2 = np.array(color_data[9:12])
                   
                    mask1 = cv2.inRange(hsv, lower1, upper1)
                    mask2 = cv2.inRange(hsv, lower2, upper2)
                    mask = cv2.bitwise_or(mask1, mask2)
                else:
                    # 默认红色范围
                    mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
                    mask2 = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
                    mask = cv2.bitwise_or(mask1, mask2)
            else:
                # 其他颜色处理
                if len(color_data) == 2:
                    # 格式: [(H_min,S_min,V_min),(H_max,S_max,V_max)]
                    lower, upper = color_data
                    print(f"调试: {color}的HSV范围: {lower} - {upper}")
                    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                elif len(color_data) == 6:
                    # 格式: [H_min,S_min,V_min,H_max,S_max,V_max]
                    lower = np.array(color_data[:3])
                    upper = np.array(color_data[3:])
                    print(f"调试: {color}的HSV范围: {lower} - {upper}")
                    mask = cv2.inRange(hsv, lower, upper)
        else:
            print(f"调试: 未找到{color}的HSV范围配置")
        
        # 调试掩码信息
        mask_non_zero = cv2.countNonZero(mask)
        print(f"调试: {color}的掩码非零像素数: {mask_non_zero}")
        
        # 简化的形态学处理
        mask = cv2.dilate(mask, self.kernel, iterations=1)
        mask = cv2.erode(mask, self.kernel, iterations=1)
        
        # 查找轮廓，筛选球体目标
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        targets = []  # 存储(中心x, 中心y, 距离)元组
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            # 过滤小噪点
            if area < self.min_contour_area:
                continue
            
            # 计算圆形度
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # 圆形度筛选
            if circularity > self.circularity_threshold:
                # 计算中心坐标
                M = cv2.moments(cnt)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # 获取外接矩形计算直径
                    x, y, w, h = cv2.boundingRect(cnt)
                    ball_diameter_pixels = max(w, h)
                    
                    # 计算距离
                    distance = self.calculate_distance(ball_diameter_pixels)
                    
                    if distance < float('inf'):
                        targets.append((cx, cy, distance))
        
        # 按距离排序
        targets.sort(key=lambda x: x[2])
            
        return targets, mask

    def detect_safe_zone(self, frame, team_color=None):
        """简化的安全区检测"""
        # 应用高斯滤波
        blurred_frame = cv2.GaussianBlur(frame, self.gaussian_blur_ksize, self.gaussian_blur_sigma)
        
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        
        # 创建安全区掩码 - 默认检测红蓝色
        red_mask1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        red_mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        blue_mask = cv2.inRange(hsv, np.array([110, 120, 70]), np.array([130, 255, 255]))
        safe_mask = cv2.bitwise_or(red_mask, blue_mask)
        
        # 简单形态学处理
        safe_mask = cv2.dilate(safe_mask, self.kernel, iterations=1)
        safe_mask = cv2.erode(safe_mask, self.kernel, iterations=1)
        
        # 查找轮廓
        contours, _ = cv2.findContours(safe_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        safe_zone = None
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_contour_area * 2:  # 安全区通常比球体大
                continue
            
            # 获取外接矩形
            x, y, w, h = cv2.boundingRect(cnt)
            
            # 简化的安全区判断 - 寻找较大的区域
            if w > 50 and h > 20:  # 假设安全区有一定的大小
                safe_zone = (x, y, w, h)
                break  # 找到第一个符合条件的区域就返回
        
        return safe_zone
    
