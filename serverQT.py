import cv2
import sys
import numpy
import struct
import time
import pickle
import gc
import socket
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap


def recvall(sock, n):
        # Функция для получения n байт или возврата None если получен EOF
        data = b''
        while len(data) < n:
            packet = sock.recv(n)
            if not packet:
                return None
            data += packet
        
        return data
    
def recv_msg(sock):
        # Получение длины сообщения и распаковка в integer
        raw_msglen = recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('<I', raw_msglen)[0]
        # Получение данных
        return recvall(sock, msglen)

    
class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    
    def run(self):
        data = b""
        payload_size = struct.calcsize("L") 
        while True:
            while len(data) < payload_size:
                data += conn.recv(4096)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += conn.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]
    ###
	
            frame=pickle.loads(frame_data)
            frame=cv2.imdecode(frame, 1)
			
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
            gc.collect()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 50
        self.top = 50
        self.width = 300
        self.height = 300
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(900, 900)
        # create a label
        self.label = QLabel(self)
        self.label.move(100, 100)
        self.label.resize(640, 480)
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()

TCP_IP = ''
TCP_PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
conn, addr = s.accept()
print("connected")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
