import os
os.environ["BLINKA_FT232H"] = "1"
import time
import board
import digitalio
import random
import numpy as np
import cv2
import dxcam
from win32api import GetSystemMetrics

fov = 17
width = GetSystemMetrics (0)
height = GetSystemMetrics (1)
left, top = (width - fov) // 2, (height - fov) // 2
right, bottom = left + fov, top + fov
region = (left, top, right, bottom)
targetFPS = 100
scanned = 0

lowerHSV = np.array([140, 90, 140])
upperHSV = np.array([150, 159, 255])


#setting the gpio pin of the mouse and the specs of the "camera"
camera = dxcam.create(output_idx=0, region = region, output_color="BGR")
camera.start(target_fps=targetFPS)
m1 = digitalio.DigitalInOut(board.C0)
m1.direction = digitalio.Direction.OUTPUT
m1.value = True
button = digitalio.DigitalInOut(board.C4)
button.direction = digitalio.Direction.INPUT


#the function which scans an image for purple
def scan(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Checking for the hue, saturation, and value
    mask = cv2.inRange(hsv, lowerHSV, upperHSV)
    return np.any(mask)


while True:
    if scan(np.array(camera.get_latest_frame())):
        if (not button.value):
            print("click")
            m1.value = False
            time.sleep(0.1 * random.random())
            m1.value = True
            time.sleep(0.4 * random.random())
