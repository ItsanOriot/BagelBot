#for use on humanbenchmark
#My low-spec pc gets on average 50-60ms with valorant open
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

fov = 20
left, top = (1920 - fov) // 2, (1080 - fov) // 2
right, bottom = left + fov, top + fov
region = (left, top, right, bottom)
targetFPS = 100
scanned = 0

#lowerHSV = np.array([140, 111, 140])
#upperHSV = np.array([148, 154, 194])

lowerRGB = np.array([0, 200, 0])
upperRGB = np.array([150, 255, 150])


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
    #hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Checking for the hue, saturation, and value
    mask = cv2.inRange(image, lowerRGB, upperRGB)
    return np.any(mask)


while True:
    if scan(np.array(camera.get_latest_frame())):
        if (not button.value):
            print("click")
            m1.value = False
            time.sleep(0.1 * random.random())
            m1.value = True
            time.sleep(0.1 * random.random())
