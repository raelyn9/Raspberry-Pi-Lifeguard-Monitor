import json
import numpy as np
import cv2

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

def getContours(mask):
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours

def getMeasure(section):
    x = config['ZONE'][section]['X']
    y = config['ZONE'][section]['Y']
    w = config['ZONE'][section]['W']
    h = config['ZONE'][section]['H']

    return x,y,w,h