"""在本地电脑运行"""
import socket
import cv2
import numpy as np


class ReceiveImg(object):
    def __init__(self, host, port):
        """初始化
        * host: 树莓派的IP地址
        * port: 端口号，与树莓派设置的端口号一致"""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)					# 设置创建socket服务的Client客服务的参数
        self.client_socket.connect((host, port))												# 连接的主机IP地址和端口
        self.connection = self.client_socket.makefile('rb')										# 创建一个makefile传输文件，读功能，读数据是b''二进制类型
        # need bytes here
        self.stream_bytes = b' '											# 创建一个变量，存放的数据类型是b''二进制类型数据
        
        print(" ")
        print("已连接到服务端：")
        print("Host : ", host)
        print("请按‘q’退出图像传输!")

    def read(self):
        try:
            msg = self.connection.read(1024)						# 读makefile传输文件，一次读1024个字节
            self.stream_bytes += msg
            first = self.stream_bytes.find(b'\xff\xd8')					# 检测帧头位置
            last = self.stream_bytes.find(b'\xff\xd9')					# 检测帧尾位置

            if first != -1 and last != -1:
                jpg = self.stream_bytes[first:last + 2]					# 帧头和帧尾中间的数据就是二进制图片数据（编码后的二进制图片数据，需要解码后使用）
                self.stream_bytes = self.stream_bytes[last + 2:]				# 更新stream_bytes数据
                image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)			# 将二进制图片数据转换成numpy.uint8格式（也就是图片格式）数据，然后解码获得图片数据
                return image

        except:
            print("Error：连接出错！")


if __name__ == '__main__':
    # TODO: 将下面的IP地址改为发送端的IP地址
    reveiver = ReceiveImg('192.168.137.112', 8000)
    while True:
        img = reveiver.read()
        if img is None:
            continue
        cv2.imshow('ori', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
