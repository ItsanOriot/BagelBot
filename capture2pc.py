import os
os.environ["BLINKA_FT232H"] = "1"
import time
import board
import digitalio
import random
import time
from io import BytesIO
import numpy as np
import concurrent.futures
import cv2


fovW = 20
fovH = 20
y = 350
x = 630
lowerHSV = np.array([140, 50, 60])
upperHSV = np.array([148, 154, 194])


#setting the gpio pin of the mouse and the specs of the "camera"
camera = cv2.VideoCapture(0)
camera.set(3, 1280) #width
camera.set(4, 720) #height
camera.set(5, 30)  #frame rate

m1 = digitalio.DigitalInOut(board.C0)
m1.direction = digitalio.Direction.OUTPUT
m1.value = True
button = digitalio.DigitalInOut(board.C4)
button.direction = digitalio.Direction.INPUT


#the function which scans an image for purple
def scan(image):
    #cropping the image and preparing for the mask
    crop = image[y:y+fovH, x:x+fovW]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    # Checking for the hue, saturation, and value
    mask = cv2.inRange(hsv, lowerHSV, upperHSV)
    condition = np.any(mask)

    return condition

with concurrent.futures.ThreadPoolExecutor() as executor:
    while True:
        ret, frame = camera.read()
        if scan(frame):
            if (not button.value):
                print("click")
                m1.value = False
                time.sleep(0.1 * random.random())
                m1.value = True
                time.sleep(0.1 * random.random())
