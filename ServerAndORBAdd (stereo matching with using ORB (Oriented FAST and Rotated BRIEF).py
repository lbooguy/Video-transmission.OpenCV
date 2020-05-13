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


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    
    def run(self):
        data = b""
        payload_size = struct.calcsize("L")
        orb = cv2.ORB_create()
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
            
            frame=pickle.loads(frame_data)
            frame=cv2.imdecode(frame, 1)


            img1 = frame[:,:320] #queryimage # left image
            img2 = frame[:, 320:] #trainimage # right image
# find the keypoints and descriptors with ORB
            kp1, des1 = orb.detectAndCompute(img1,None)
            kp2, des2 = orb.detectAndCompute(img2,None)
# create BFMatcher object
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
# Match descriptors.
            matches = bf.match(des1,des2)
# Sort them in the order of their distance.
            matches = sorted(matches, key = lambda x:x.distance)
# Draw first 10 matches.
            img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
          #  plt.imshow(img3)#,plt.show()
            frame=img3
            
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
        self.label.move(10, 10)
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
