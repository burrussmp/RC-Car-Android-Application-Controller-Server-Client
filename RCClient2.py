from ctypes import windll, Structure, c_long, byref
import sys
import time
import socket
from threading import Thread
import threading
import logging
import sys
import numpy as np
import time
import math
#import psutil
import cv2
idle_dcTuple = (15,15) # (steering,acceleration) # note steering may need to be adjusted, yet the range should stay at 10.
# MUTABLE"
server_address_data = ('192.168.1.85',5001)
server_address_camera = ('192.168.1.85',5002)
forward_Range = 0.6 # %python

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}

def initializeConnection(server_address,idle_dcTuple):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    miny = 10
    maxy = 20
    signal = (miny,maxy)
    message = str(signal)
    sock.sendall(message.encode())
    data = sock.recv(16)

def cameraThread(sock):
    while 1:
        message = "PASSWORD=987654321"
        sent = sock.sendto(message.encode(), server_address_camera)
        data, addr = sock.recvfrom(30000)
        nparr = np.fromstring(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imshow('Live Feed',frame)
        cv2.waitKey(1)
    release(cap)

def dataThread(sock):
    acc = 15.63
    while 1:
        steering,acceleration = mousePosToDutyCycle()
        message = "PASSWORD=123456789;STEERING="+str(steering)+";ACCELERATION="+str(acceleration)
        sent = sock.sendto(message.encode(), server_address_data)
def mousePosToDutyCycle():
    pos = queryMousePosition()
    minXPos = 0 #left
    maxXPos = 1365 #right
    minYPos = 0 # top
    maxYPos = 767 #bottom
    normX = (pos['x']-minXPos)/(maxXPos-minXPos)
    normY = (pos['y'] - minYPos)/(maxYPos-minYPos)
    # denormalize to steering
    steering = (20-10)*normX + 10
    acceleration = forward_Range*normY + idle_dcTuple[1]
    return steering,acceleration
       
# MAIN
if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cameraThread = Thread(target = cameraThread,args = (sock,))
    cameraThread.start()
    dataThread = Thread(target=dataThread,args = (sock,))
    dataThread.start()