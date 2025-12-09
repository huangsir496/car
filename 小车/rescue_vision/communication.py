import serial
import cv2
import time

def main():
    # 配置串口参数
    port = 'COM3'  # 在Windows上是'COM3'
    baudrate = 115200
    ser = open_serial_port(port, baudrate)
    if not ser.isOpen():
        print("无法打开串口")
        retur
    print("串口已打开")
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    print("摄像头已打开")
    
    while True:
        # 读取一帧图像
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头")
            break
        
        # 处理图像（例如，显示）
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按'q'退出循环
            break
        
        # 发送数据到串口（例如每帧）
        send_data_via_serial(ser, "Frame captured!")
    cap.release()  # 释放摄像头资源
    ser.close()  # 关闭串口资源
    cv2.destroyAllWindows()  # 关闭所有OpenCV窗口

if __name__ == "__main__":
    main()
