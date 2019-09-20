import cv2
import numpy as np
from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
from time import sleep
import os
import smtplib

import utility_pi as util


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
args = vars(ap.parse_args())

# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()

# initial settings
class Section():
    def __init__(self,name):
        self.name = name
        self.status = ""
        self.start = ""
        self.duration = ""
        self.record = ""
        self.email = True

sectionA = Section("SECTION_A")
sectionB = Section("SECTION_B")
sectionC = Section("SECTION_C")
sectionD = Section("SECTION_D")

def recordStatus(section,status):
    if section.status != status:
        with open('record.txt', 'a') as f:
            end_time = timestamp
            # if first time, then skip
            if section.status != "":
                duration = end_time - section.start_time
                dur_sec = int(duration.total_seconds())
                if (dur_sec < 2):
                    return
                section.record = section.record+','+end_time.strftime('%Y-%m-%d %H:%M:%S')+','+str(dur_sec)+'\n'
                f.write(section.record)
                print(section.record)
                section.record = ""

            section.start_time = end_time
            section.status = status
            section.record = section.name+','+section.status+','+section.start_time.strftime('%Y-%m-%d %H:%M:%S')


def findContours(frame,section):

    status = "Unoccupied"

    x,y,w,h = util.getMeasure(section.name)
    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    roi = frame[y:y+h, x:x+w]
    mask = util.getRedMask(roi)
    object_contours = util.getContours(mask)

    for contour in object_contours:
        area = cv2.contourArea(contour)
        if area > 100:
            cv2.drawContours(roi, contour, -1, (0, 255, 0), 3)
            status = "Occupied"

    cv2.putText(roi, "{}: {}".format(section.name,status), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    recordStatus(section,status)


# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array
    timestamp = datetime.datetime.now()

    # resize the frame
    frame = imutils.resize(frame, width=1000)

    mask = util.getRedMask(frame)

    findContours(frame,sectionA)
    findContours(frame,sectionB)
    findContours(frame,sectionC)
    findContours(frame,sectionD)

    # check to see if the frames should be displayed to screen
    if conf["show_video"]:
        # display the security feed
        cv2.imshow("Security Feed", frame)
        cv2.imshow("Mask", mask)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

cv2.destroyAllWindows()
