#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import deque
import numpy as np
import argparse
import cv2
import time
import imutils
x = 0 #programın ileride hata vermemesi için x 0 olarak tanımlıyorum
y = 0 # programın ileride hata vermemesi için y 0 olarak tanımlıyorum
radius = 0

#GPIO
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Pin definitions
rightFwd = 35
rightRev = 37
leftFwd = 40
leftRev = 33
en = 25

#GPIO initialization
defaultSpeed = 50
GPIO.setup(leftFwd, GPIO.OUT)
GPIO.setup(leftRev, GPIO.OUT)
GPIO.setup(rightFwd, GPIO.OUT)
GPIO.setup(rightRev, GPIO.OUT)
GPIO.setup(en,GPIO.OUT)

#Disable movement at startup
GPIO.output(leftFwd, False)
GPIO.output(leftRev, False)
GPIO.output(rightFwd, False)
GPIO.output(rightRev, False)

#PWM Initialization

rightMotorFwd = GPIO.PWM(rightFwd, 50)
leftMotorFwd = GPIO.PWM(leftFwd, 50)
rightMotorRev = GPIO.PWM(rightRev, 50)
leftMotorRev = GPIO.PWM(leftRev, 50)
rightMotorFwd.start(defaultSpeed)
leftMotorFwd.start(defaultSpeed)
leftMotorRev.start(defaultSpeed)
rightMotorRev.start(defaultSpeed)

def updatePwm(rightPwm, leftPwm):
     rightMotorFwd.ChangeDutyCycle(rightPwm)
     leftMotorFwd.ChangeDutyCycle(leftPwm)

def pwmStop():
     rightMotorFwd.ChangeDutyCycle(0)
     rightMotorRev.ChangeDutyCycle(0)
     leftMotorFwd.ChangeDutyCycle(0)
     leftMotorRev.ChangeDutyCycle(0)


#rengin algılanması
colorLower = (20, 100, 100)
colorUpper = (40, 255, 255)
#converter.py ile convert ettiğiniz rengi buraya giriniz
camera = cv2.VideoCapture(0) #  webcamin bagli oldugu port varsayilan 0
camera.set(15, -10)

while True: #yazılımımız çalıştığı sürece aşağıdaki işlemleri tekrarla
     
     (grabbed, frame) = camera.read() # grabbed ve frame değişkenini camera.read olarak tanımlıyoruz.


     frame = imutils.resize(frame, width=320, height=240) # görüntü genişliğini ayarlıyorum
     frame = imutils.rotate(frame, angle=0) # görüntüyü sabitliyoruz

     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # görüntüyü hsv formatına çeviriyoruz
     mask = cv2.inRange(hsv, colorLower, colorUpper) # hsv formatına dönen görüntünün bizim belirttiğimiz renk sınırları içerisinde olanları belirliyor
     mask = cv2.erode(mask, None, iterations=2) # bizim renklerimizi işaretliyor
     mask = cv2.dilate(mask, None, iterations=2) # bizim renklerimizin genişliğini alıyor


     cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	 cv2.CHAIN_APPROX_SIMPLE)[-2]
     center = None


     if len(cnts) > 0:

               c = max(cnts, key=cv2.contourArea)
               ((x, y), radius) = cv2.minEnclosingCircle(c)
               M = cv2.moments(c)
               center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))


               if radius > 10: #algılanacak hedefin minumum boyutu
                    cv2.circle(frame, (int(x), int(y)), int(radius),
				 (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
     else:
          x = 0
          y = 0
          r = 0

     print("x : ")
     print(x) # kameradan gelen görüntüde bizim rengimiz varsa x kordinatı
     print("y : ")
     print(y) # kameradan gelen görüntüde bizim rengimiz varsa y kordinatı
     print("r : ")
     print(radius)
     cv2.imshow("test", frame)
     if cv2.waitKey(1) & 0xFF == ord('q'):
          break    
     
     if x == 0:
          pwmStop()

     if radius != 0 and 60 > radius > 10 and 0 < x < 120:
          print("sola dön")
          GPIO.output(leftFwd, GPIO.HIGH)
          GPIO.output(leftRev, GPIO.LOW)


     elif radius != 0 and 60 > radius > 10 and 200 < x < 320:
          print("sağa dön")
          GPIO.output(rightFwd, GPIO.HIGH)
          GPIO.output(rightRev, GPIO.LOW)


     elif radius != 0 and 60 > radius > 10 and 120 < x < 200:
          print("ilerle")
          GPIO.output(leftFwd, GPIO.HIGH)
          GPIO.output(leftRev, GPIO.LOW)
          GPIO.output(rightFwd, GPIO.HIGH)
          GPIO.output(rightRev, GPIO.LOW)

     else:
          pass
