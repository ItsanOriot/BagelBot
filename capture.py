#imports
from picamera import PiCamera
import random
import RPi.GPIO as GPIO
import time
from io import BytesIO
import numpy as np
import concurrent.futures

#setting the gpio pin of the mouse and the specs of the "camera"
camera = PiCamera()
camera.resolution = (864, 480)
camera.framerate = 50
camera.zoom = (0.493,0.48,0.014,0.04)
time.sleep(2)

#setting up the led for registering clicks
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.output(18,GPIO.HIGH)
GPIO.setup(17, GPIO.IN)

#camera.start_preview()

#the function which scans an image for purple
def scan(image):
    # Checking for the right colors
    conditionColors = np.any((image[..., 0] > 209) & (np.logical_and(image[..., 1] > 50, image[..., 1] < 128)) & (image[..., 2] > 162))
    return conditionColors
    

with concurrent.futures.ThreadPoolExecutor() as executor:
    stream = BytesIO()
    for _ in camera.capture_continuous(stream, format='rgb', use_video_port=True):
            stream.seek(0)
            image = np.frombuffer(stream.getvalue(), dtype=np.uint8)
            image = image.reshape((480, 864, 3))
            if scan(image):
                if not GPIO.input(17):
                    print("click")
                    GPIO.output(18, GPIO.LOW)
                    time.sleep(0.06 * random.random())
                    GPIO.output(18, GPIO.HIGH)
                    time.sleep(0.08 * random.random())
            stream.seek(0)
            stream.truncate()
