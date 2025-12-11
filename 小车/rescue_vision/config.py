#相机设置
CAMERA_CONFIG = {
    "resolution": (640, 480),  # 相机分辨率
    "horizontal_fov": 60,       # 水平视场角（度），听说这个可以不用设置
               }

# 目标参数配置
TARGET_CONFIG = {
    "known_ball_diameter": 40,  # 已知球体直径（mm），配置方法：使用卡尺测量实际球的直径
    "min_contour_area": 20,     # 最小轮廓面积（像素），配置方法：在目标最小距离下测试并调整，过滤噪点
    "circularity_threshold": 0.65, # 圆形度阈值，配置方法：范围0-1，值越大越严格要求圆形，推荐0.6-0.8
}

# 颜色HSV阈值配置
#特别注意红色是两个范围的
COLOR_RANGES = {
    "red": [0, 153, 77, 11, 255, 255, 150, 30, 50, 180, 255, 255],  # red目标，配置方法：在实际环境下调整H值
    "blue": [88, 146, 61, 179, 255, 255],  # blue目标，配置方法：在实际环境下调整H值
    "black": [(0, 0, 0), (179, 255, 46)],  # black目标，配置方法：在实际环境下调整H值
    "yellow": [19, 111, 78, 63, 237, 226],  # yellow目标，配置方法：在实际环境下调整H值
    "white": [(0, 0, 200), (180, 255, 255)],  # white目标，配置方法：在实际环境下调整H值
}



# 视觉处理配置，这里很多设置都是多余的，用于测试用的代码
VISION_CONFIG = {
    "display_result": True,     # 是否显示处理结果，配置方法：True显示实时图像，False不显示可提高性能
    "debug_mode": True,         # 是否启用调试模式，配置方法：True输出详细信息，False静默运行
    "morph_kernel_size": (5, 5), # 形态学处理内核大小，配置方法：(3,3)轻量处理，(5,5)标准，(7,7)强力
    "erode_iterations": 1,      # 腐蚀迭代次数，配置方法：增加可去除小噪声，但会缩小目标
    "dilate_iterations": 2,     # 膨胀迭代次数，配置方法：增加可连接断开的轮廓，使目标更完整
    "gaussian_blur_ksize": (5, 5), # 高斯滤波内核大小，配置方法：必须为奇数，值越大模糊效果越强
    "gaussian_blur_sigma": 0,   # 高斯滤波标准差，配置方法：0自动计算，或手动设置正数
    "ball_distance_scale": 15000,  # 距离计算缩放因子，配置方法：根据实际测试校准
    "ball_distance_offset": 0,     # 距离计算偏移量，配置方法：根据实际测试校准
}

# 安全区检测配置
#这个还有待测量
SAFE_ZONE_CONFIG = {
    "aspect_ratio_min": 2,      # 最小长宽比
    "aspect_ratio_max": 4,      # 最大长宽比
    "min_area": 500,            # 最小面积（像素）
    "max_area": 50000,          # 最大面积（像素）
}