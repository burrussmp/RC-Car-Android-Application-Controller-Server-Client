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
server_address_data = ('10.66.70.119',4597)
server_address_camera = ('10.66.70.119',4579)
forward_Range = 2 # %python

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}

def cameraThread(sock):
    while 1:
        message = "PASSWORD=9876;TYPE="
        sent = sock.sendto(message.encode(), server_address_camera)
        print("sent")
        data, addr = sock.recvfrom(50000)
        nparr = np.fromstring(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        try:
            cv2.imshow('Live Feed',frame)
        except:
            print("empty image")
        cv2.waitKey(33)


    release(cap)

def dataThread(sock):
    acc = 15.63
    while 1:
        steering,acceleration = mousePosToDutyCycle()
        message = "PASSWORD=1234;STEERING="+str(steering)+";ACCELERATION="+str(acceleration)
        sent = sock.sendto(message.encode(), server_address_data)
        time.sleep(0.33)
        
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
    acceleration = forward_Range*normY + idle_dcTuple[1]-1
    return steering,acceleration
       
# MAIN
if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cameraThread = Thread(target = cameraThread,args = (sock,))
    cameraThread.start()
    dataThread = Thread(target=dataThread,args = (sock2,))
    dataThread.start()