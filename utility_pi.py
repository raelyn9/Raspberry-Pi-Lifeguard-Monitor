import json
import numpy as np
import cv2
import imutils

class Section():
    def __init__(self):
        self.status = ""
        self.start = ""
        self.duration = ""
        self.email = True


# read params from config.json
with open('config.json', 'r') as f:
    config = json.load(f)


def getMask(frame,color):

    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    lower = np.array(config['COLOR'][color]['LOW'])
    upper = np.array(config['COLOR'][color]['HIGH'])
    mask = cv2.inRange(hsv, lower, upper)
    return mask

def getRedMask(frame):
    red_mask1 = getMask(frame,"RED_LOW")
    red_mask2 = getMask(frame,"RED_HIGH")
    mask = cv2.bitwise_or(red_mask1, red_mask2)
    return mask

def getContours(mask):
    contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = contours[0] if imutils.is_cv2() else contours[1]
    return contours

def getMeasure(section):
    x = config['ZONE'][section]['X']
    y = config['ZONE'][section]['Y']
    w = config['ZONE'][section]['W']
    h = config['ZONE'][section]['H']

    return x,y,w,h