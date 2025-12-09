import serial
import serial.tools.list_ports
import sys
import select
serial_port = "/dev/ttyS0" # 串口设备路径（系统实际存在的串行端口）
baud_rate = 9600     # 波特率

exit_key=' '    # 触发关闭串口的按键（空格键）
try:
    
    ser = serial.Serial(serial_port, baud_rate, timeout=0.1)

    if ser.is_open:
        print("串口已打开")
        data = ser.read_all().decode('utf-8', errors='ignore')
        print(f"读取到的数据: {data}")

        if data:
            response_data = bytes([1, 1])
            ser.write(response_data)
            print("已发送响应数据: [1, 1]")
    else:
        print("串口未打开或者读取错误")

finally:
    if select.select([sys.stdin], [], [], 0.01)[0]:
            key = sys.stdin.read(1)  # 读取按下的按键
            if key == exit_key:  # 按下空格键
                print(f"\n检测到【{exit_key}】键，准备关闭串口...")
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("串口已关闭")
  # 用于非阻塞监听键盘输入（不影响串
    