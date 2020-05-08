import socket
import cv2
import numpy
import time
import pickle
import struct

TCP_IP = '192.168.1.44'
TCP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

capture = cv2.VideoCapture(0)
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),10]
while True:
    ret, frame = capture.read()


    if ret:
        result,imgencode=cv2.imencode('.jpeg',frame,encode_param)
        data=pickle.dumps(imgencode)
        # print(data.__sizeof__())
        sock.sendall(struct.pack("L",len(data))+data)
        time.sleep(0.01)
    else:
        break
 

  

 