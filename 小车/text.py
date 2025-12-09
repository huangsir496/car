import serial
import serial.tools.list_ports
import sys
import select  # 用于非阻塞监听键盘输入（不影响串口接收）
import time  # 用于添加延时和自动退出

# -------------------------- 配置参数（按你的场景修改）--------------------------
# 树莓派4串口路径（二选一）
# serial_port = "/dev/ttyUSB0"  # 外接USB串口模块（推荐）
# serial_port = "/dev/ttyAMA0"  # 板载GPIO串口（需先切换映射）
serial_port = "/dev/ttyS0"  # 系统实际存在的串口

baud_rate = 9600  # 必须和电控的波特率一致！
timeout = 0.1     # 串口读取超时时间（秒）
exit_key = ' '    # 触发关闭串口的按键（空格键）
auto_exit_time = 5  # 自动退出时间（秒），用于演示

# -------------------------- 自动列出可用串口（调试用）--------------------------
print("树莓派4可用串口列表：")
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"  - 路径：{port.device} | 描述：{port.description}")
print(f"\n提示：串口已打开，持续接收电控数据... 按【{exit_key}】键关闭串口\n")

try:
    print(f"尝试打开串口：{serial_port}，波特率：{baud_rate}")
    # 打开串口（独占模式，避免被其他进程占用）
    ser = serial.Serial(
        port=serial_port,
        baudrate=baud_rate,
        timeout=timeout,
        exclusive=True
    )

    if ser.is_open:
        print(f"✅ 成功打开串口：{serial_port}")
        print(f"串口参数：端口={ser.port}, 波特率={ser.baudrate}, 超时={ser.timeout}秒")
    else:
        print("❌ 错误：串口未成功打开！")
        sys.exit(1)

    # 记录开始时间
    start_time = time.time()
    
    # 循环接收数据，直到按下空格键或超时
    while True:

          
        
        # 1. 实时读取串口数据（电控发送的信息）
        try:
            if ser.in_waiting > 0:  # 检测是否有数据待读取
                data = ser.read_all().decode('utf-8', errors='ignore')
                if data:
                    print(f"收到电控数据：{data.strip()}")  # strip() 去除多余换行/空格
                    respond="[1,1]"
                   
                    ser.write(respond.encode('utf-8'))  # 回传数据给电控
                    print(f"已回传数据给电控：{respond}")
        except Exception as e:
            print(f"读取串口数据时出错：{e}")

        # 2. 非阻塞监听键盘输入（不影响串口接收）
        # 检测是否有键盘按键按下（超时0.01秒，快速响应）
        try:
            if select.select([sys.stdin], [], [], 0.01)[0]:
                key = sys.stdin.read(1)  # 读取按下的按键
                if key == exit_key:  # 按下空格键
                    print(f"\n检测到【{exit_key}】键，准备关闭串口...")
                    break  # 退出循环，执行关闭操作
        except Exception as e:
            print(f"监听键盘输入时出错：{e}")
        
        # 添加短暂延时，减少CPU占用
        time.sleep(0.1)

except serial.SerialException as e:
    print(f"\n❌ 串口错误：{e}")
    print("解决建议：1. 确认路径正确；2. 配置dialout权限（sudo usermod -aG dialout pi）；3. 检查电控是否断电/接线松动")
except KeyboardInterrupt:
    print("\n\n程序被强制中断（如Ctrl+C），正在关闭串口...")
except Exception as e:
    print(f"\n❌ 未预期的错误：{e}")
finally:
    # 确保串口最终关闭
    print("\n进入finally块，准备关闭串口...")
    if 'ser' in locals():
        if ser.is_open:
            try:
                ser.close()
                print("✅ 串口已成功关闭")
            except Exception as e:
                print(f"❌ 关闭串口时出错：{e}")
        else:
            print("⚠️  串口未处于打开状态")
    else:
        print("⚠️  串口对象未创建")
    print("程序已退出")
    sys.exit(0)