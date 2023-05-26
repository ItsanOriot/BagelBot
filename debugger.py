import time
import random
import numpy as np
import cv2
import dxcam
from win32api import GetSystemMetrics

fov = 150
left, top = (1920 - fov) // 2, (1080 - fov) // 2
right, bottom = left + fov, top + fov
region = (left, top, right, bottom)
targetFPS = 100
scanned = 0

lowerHSV = np.array([140, 90, 140])
upperHSV = np.array([150, 159, 255])


#setting the gpio pin of the mouse and the specs of the "camera"
camera = dxcam.create(output_idx=0, region = region, output_color="BGR")
camera.start(target_fps=targetFPS)


#the function which scans an image for purple


while True:
    image = np.array(camera.get_latest_frame())
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerHSV, upperHSV)
    # Display the resulting frame
    cv2.imshow('Video', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
camera.release()
cv2.destroyAllWindows()
