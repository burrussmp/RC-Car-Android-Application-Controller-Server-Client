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
#import IO
import logging
from queue import Queue

server_address_data = ('192.168.1.85',5001)
server_address_camera = ('192.168.1.85',5002)
miny=0
maxy=0
speed = 0

class protocol(object):
    def __init__(self, message):
        self.mPasswordControl = "123456789"
        self.mPasswordView = "987654321"
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
        acc = float(self.messageComponents["ACCELERATION"])
        return (steer,acc)

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

def cameraThread(sock):
    cap = configureCamera(320,240,30)  
    ret = True
    while ret:
        ret, frame = cap.read()
        data, address = sock.recvfrom(4096)
        data_decoded = data.decode()
        viewer = protocol(data_decoded)
        if (viewer.isAuthorizedtoView()):
            data = cv2.imencode('.jpg', frame)[1].tostring()
            size = str(sys.getsizeof(data))
            sock.sendto(data, address)
        else:
            print("Unauthorized viewer: %s" % (address,))
    release(cap)

def dataThread(sock):
    acc = 15.63
    #IO.changeDutyCycle((15, 15))
    while 1:
        data, addr = sock.recvfrom(1024)
        data_decoded = data.decode()
        controller = protocol(data_decoded)   
        if (controller.isAuthorizedToControl()):
            print(controller.getControl())
            #IO.changeDutyCycle(p1.getControl)
        else:
            print("Not authorized: Invalid Password")
            #IO.changeDutyCycle((15, 15))

if __name__=="__main__":
    sockCamera = createSocket(server_address_camera)
    sockData = createSocket(server_address_data)
    #IO.initGPIO(100,0,0) # freq = 100 Hz, duty cycle = 0 for both acc and steering
    logging.basicConfig(filename='scheduler.log', level=logging.DEBUG, filemode='w') 
    cameraThread = Thread(target = cameraThread,args = (sockCamera,))
    cameraThread.start()
    dataThread = Thread(target=dataThread,args = (sockData,))
    dataThread.start()
