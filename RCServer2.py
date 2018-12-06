# RCServer.py
# author: Matthew P. Burruss
# last update: 8/14/2018
# Description: Main function

import socket
import numpy as np
from datetime import datetime
import time
from threading import Thread
import threading
from ast import literal_eval as make_tuple
import math
import cv2
import csv
import psutil
import sys
import IO
### REMEMBER THAT THE CLIENT CHANGED SIZE OF THE BYTES IT SENDS/RECEIVES
import logging
from queue import Queue

server_address_data = ('10.66.56.155',4597)
server_address_camera = ('10.66.56.155',4579)
#server_address_data = ('10.66.65.165',4597)
#server_address_camera = ('10.66.65.165',4579)

miny=0
maxy=0
speed = 0

class protocol(object):
    def __init__(self, message):
        self.mPasswordControl = "1234"
        self.mPasswordView = "9876"
        self.messageComponents = {}
        components = message.count('=')
        keyStart = 0
        for i in range(components):
            keyEnd = message.find('=',keyStart)
            valueStart = keyEnd+1
            valueEnd = message.find(';',valueStart)
            if (valueEnd == -1):
                valueEnd = len(message)
            self.messageComponents[message[keyStart:keyEnd]]=message[valueStart:valueEnd]
            keyStart=valueEnd+1
    def isAuthorizedToControl(self):
        return (self.messageComponents["PASSWORD"] == self.mPasswordControl)
    def isAuthorizedtoView(self):
        return (self.messageComponents["PASSWORD"] == self.mPasswordView)
    def getControl(self):
        steer = float(self.messageComponents["STEERING"])
        steer = float("{0:.2f}".format(steer))
        acc = float(self.messageComponents["ACCELERATION"])
        acc = float("{0:.2f}".format(acc))
        return (steer,acc)
    def getImageType(self):
        return self.messageComponents["TYPE"]
def cleanup(sock,connection=0):
    IO.cleanGPIO()
    sock.close()
    if (connection != 0):
        connection.close()

def createSocket(server_address):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    return sock

def release(cap):
    print('Releasing')
    cap.release()

def configureCamera(width,height,fps):
    cap = cv2.VideoCapture(0)
    cap.set(int(3),width)
    cap.set(int(4),height)
    cap.set(int(5),fps)
    return cap
def preprocess(img):
    img = cv2.resize(img, (200, 66))
    return img

def cartoonize(img_color):
    num_down = 2       # number of downsampling steps
    num_bilateral = 7  # number of bilateral filtering steps
    img_rgb = img_color
    for _ in  range(num_down):
        img_color = cv2.pyrDown(img_color)
    for _ in range(num_bilateral):
        img_color = cv2.bilateralFilter(img_color, d=9,
                                        sigmaColor=9,
                                        sigmaSpace=7)
    for _ in range(num_down):
        img_color = cv2.pyrUp(img_color)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)
    img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                    cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY,
                                    blockSize=9,
                                    C=2)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    return cv2.bitwise_and(img_color, img_edge)

def lanedetect(image):
    # convert to gray
    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gauss_gray = cv2.GaussianBlur(image,(3,3),0)
    mask_white = cv2.inRange(gauss_gray, 200, 255)
    #cv2.imshow('Mask white/Gauss filter ', mask_white)

    # apply canny edge
    low_threshold = 50
    high_threshold = 125
    canny_edges = cv2.Canny(mask_white,low_threshold,high_threshold)
    #cv2.imshow('Edge detection', canny_edges)
    # canny edge
    return canny_edges
    
def cameraThread(sock):
    cap = configureCamera(320,240,30)  
    ret = True
    while ret:
        data, address = sock.recvfrom(30)
        data_decoded = data.decode()
        viewer = protocol(data_decoded)
        if (viewer.isAuthorizedtoView()):
            ret, frame = cap.read()
            if (viewer.getImageType() == "CARTOON"):
                frame = cartoonize(frame)
            elif (viewer.getImageType() == "DETECT LANE"):
                frame = lanedetect(frame)
            data = cv2.imencode('.jpg', frame)[1].tostring()
            size = str(sys.getsizeof(data))
            #print(size)
            sock.sendto(data, address)
        else:
            print("Unauthorized viewer: %s" % (address,))
    release(cap)

def dataThread(sock):
    acc = 15.63
    IO.changeDutyCycle((15, 15))
    while 1:
        data, addr = sock.recvfrom(2000)
        #response = "hi"
        #sock.sendto(response.encode(), addr)
        print(data)
        data_decoded = data.decode()
        controller = protocol(data_decoded)   
        if (controller.isAuthorizedToControl()):
            #print(controller.getControl())
            #print()
            IO.changeDutyCycle(controller.getControl())
        else:
            print("Not authorized: Invalid Password")
            IO.changeDutyCycle((15, 15))
if __name__=="__main__":
    sockCamera = createSocket(server_address_camera)
    sockData = createSocket(server_address_data)
    IO.initGPIO(100,0,0) # freq = 100 Hz, duty cycle = 0 for both acc and steering
    logging.basicConfig(filename='scheduler.log', level=logging.DEBUG, filemode='w') 
    cameraThread = Thread(target = cameraThread,args = (sockCamera,))
    cameraThread.start()
    dataThread = Thread(target=dataThread,args = (sockData,))
    dataThread.start()
