import serial
import serial.tools.list_ports

# 列出所有可用串口
ports = list(serial.tools.list_ports.comports())
for port in ports:
    print(f"设备名称: {port.device}, 描述: {port.description}")
