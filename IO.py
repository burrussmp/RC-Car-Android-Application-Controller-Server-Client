# IO.py
# author: Matthew P. Burruss

# PWM Control for Raspberry 3pi acceleration
# GPIO18: acceleration
# GPIO19: steering where [10,15] left and [15,20] right

import datetime
from datetime import datetime
import time
from ast import literal_eval as make_tuple
import pigpio
import RPi.GPIO as GPIO
import math
import csv
import os

# initialize a pigpiod object
pi = pigpio.pi()
# Duty Cycle parameters (adjustable (not recommended))
freq = 100
steering = 0
acceleration = 0

# init()
# Summary: Initializes GPIO
# Parameter: freq   => frequency of PWM signal
#            dcAcc  => duty cycle for acceleration at idle 
def initGPIO(freq,dcAcc,dcSteer):
    pi.hardware_PWM(18,freq,int(dcAcc*10000))
    pi.hardware_PWM(19,freq,int(dcSteer*10000))

# changeDutyCycle()
# Summary: Changes PWM duty cycles for steering and acceleration 
# Parameter: data => tuple of doubles containing the duty cycles (%) for steering and acceleration
def changeDutyCycle(dc):
    global steering, acceleration
    if (steering != dc[0]):
        steering = dc[0]
        #print(steering)
        pi.hardware_PWM(19,freq,int(dc[0]*10000))
    if (acceleration != dc[1]):
        acceleration = dc[1]
        #print(acceleration)
        pi.hardware_PWM(18,freq,int(dc[1]*10000))     

# cleanGPIO()
# Summary: Writes speed data to a Speed.csv, turns off Traxxas, and clears GPIO. 
def cleanGPIO():
    global timestamps,speeds
    print('Cleaning up GPIO and writing to csv file')
    GPIO.cleanup()
    pi.hardware_PWM(18,freq,0)
    pi.hardware_PWM(19,freq,0)
    pi.stop()

