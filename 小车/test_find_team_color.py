#!/usr/bin/env python3
import serial
import time

# 模拟发送[FindTeamColor]命令到串口
try:
    # 打开串口（使用与main.py相同的配置）
    ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate=115200,
        timeout=1
    )
    
    print("串口已打开")
    
    # 发送[FindTeamColor]命令
    command = "[FindTeamColor]"
    ser.write(command.encode('utf-8'))
    print(f"已发送命令: {command}")
    
    # 等待并读取响应
    time.sleep(0.1)
    if ser.in_waiting > 0:
        response = ser.read_all().decode('utf-8', errors='ignore')
        print(f"收到响应: {response.strip()}")
    
    # 关闭串口
    ser.close()
    print("串口已关闭")
    
except Exception as e:
    print(f"测试过程中出现错误: {e}")