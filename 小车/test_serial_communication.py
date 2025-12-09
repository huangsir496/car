import serial
import time

def test_serial_communication():
    # 打开串口
    try:
        ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=115200,
            timeout=1
        )
        print("串口 /dev/ttyS0 已成功打开")
    except Exception as e:
        print(f"无法打开串口: {e}")
        return
    
    try:
        # 发送[FindTeamColor]命令
        command = '[FindTeamColor]'
        print(f"发送命令: {command}")
        ser.write((command + '\n').encode('utf-8'))
        
        # 等待并读取响应
        time.sleep(0.5)
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"收到响应: {response}")
            if response == "[0,0]":
                print("警告: 响应为[0,0]，可能未检测到球")
            else:
                print("成功: 检测到球并返回有效响应")
        else:
            print("未收到响应")
            
    except Exception as e:
        print(f"串口通信错误: {e}")
    finally:
        # 关闭串口
        ser.close()
        print("串口已关闭")

if __name__ == "__main__":
    test_serial_communication()