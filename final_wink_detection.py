# Final wink detection script!!

# USAGE
# $ cd eye-blink/
# $ workon cv
# $ python final_wink_detection.py

# CV specific packages
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

import os
from os import listdir
from os.path import isfile, join

# display specific packages
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735

audioFile = "/home/pi/eye-blink/ka-ching-kurz.mp3"
starting_pic = "/home/pi/eye-blink/display/starting_face_recognition_algo.jpg"
loading_pic = "/home/pi/eye-blink/display/loading.jpg"
load_shape_predictor_pic = "/home/pi/eye-blink/display/loading_shape_predictor.jpg"
start_video_stream_pic = "/home/pi/eye-blink/display/start_video_stream.jpg"
look_into_eyes_boi_pic = "/home/pi/eye-blink/display/look_into_eyes_boi.jpg"
pepe_give_wink_pic = "/home/pi/eye-blink/display/pepe_give_wink.jpg"
pepe_miss_you_pic = "/home/pi/eye-blink/display/pepe_will_miss_you.jpg"
msc_max_pic = "/home/pi/eye-blink/display/msc_max.jpg"
msc_max_pepe_pic = "/home/pi/eye-blink/display/msc_max_pepe.jpg"

pepe_wink_gif = "/home/pi/eye-blink/display/frosch_frame"


# Function calculates the eye aspect ratio for blink determination
def eye_aspect_ratio(eye):
        # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear

# Function takes an image path as input and displays it to the lcd screen
def drawImage(imagePath):
    image = Image.open(imagePath)
    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    # Crop and center the image
    x = scaled_width / 2 - width / 2
    y = scaled_height / 2 - height / 2
    image = image.crop((x, y, x + width, y + height-6))

    # Display image.
    disp.image(image)

# function shows a gif
# gifFolderPath includes the folder path to gif frames
# inside the folder the naming for the frames must be "folderName (1).jpg", "folderName (2).jpg", etc.
def showGIF(gifFolderPath, repetitions):
    folderName = gifFolderPath.split("/")
    # find all elements in the folder and count them
    onlyfiles = [f for f in listdir(gifFolderPath) if isfile(join(gifFolderPath, f))]
    numberOfFiles = len(onlyfiles)

    for j in range(repetitions):
        for i in range(1, numberOfFiles):
            drawImage(gifFolderPath + "/" +  folderName[-1] + " (" + str(i) + ").jpg")
            time.sleep(0.05)


# Display: Configuration for CS and DC pins:
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Display backlight pin
# The backlight will be turned on
# after shutdown the backlight will turn off
display_backlight_pin = digitalio.DigitalInOut(board.D22)
display_backlight_pin.switch_to_output()
display_backlight_pin.value = True

# Display: Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Display: Setup SPI bus using hardware SPI:
spi = board.SPI()

# Display: 1.8" ST7735R
disp = st7735.ST7735R(spi, rotation=270,                           
                        cs=cs_pin,
                        dc=dc_pin,
                        rst=reset_pin,
                        baudrate=BAUDRATE)

# Display: Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

# Display: Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Display: Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)


# Connect a switch between GROUND (Pin 6) and GPIO 2
# and enable pullup resistor
switch = digitalio.DigitalInOut(board.D2)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# variables for last else statement
interval = 15000
previousTime = 0

while True:
        if switch.value == False:
                print("switch touched")
                print("Starting face recognition...")
                drawImage(starting_pic)
                time.sleep(1.5)


                # Display: First define some constants to allow easy positioning of text.
                # padding = -2
                # x = 0
                # Display: Load a TTF font.  Make sure the .ttf font file is in the
                # same directory as the python script!
                # Some other nice fonts to try: http://www.dafont.com/bitmap.php
                # font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

                
                # define two constants, one for the eye aspect ratio to indicate
                # blink and then a second constant for the number of consecutive
                # frames the eye must be below the threshold
                EYE_AR_THRESH = 0.3
                EYE_AR_CONSEC_FRAMES = 2

                # initialize the frame counters and the total number of blinks
                COUNTER = 0
                TOTAL = 0
                print("Total counter set to:", TOTAL)
                # initialize dlib's face detector (HOG-based) and then create
                # the facial landmark predictor

                drawImage(loading_pic)
                time.sleep(1)
                drawImage(load_shape_predictor_pic)

                print("[INFO] loading facial landmark predictor...")
                detector = dlib.get_frontal_face_detector()
                predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

                # grab the indexes of the facial landmarks for the left and
                # right eye, respectively
                (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
                (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

                drawImage(start_video_stream_pic)

                # start the video stream thread
                print("[INFO] starting video stream thread...")
                # vs = FileVideoStream('blink_detection_demo.mp4').start()
                # fileStream = True
                # vs = VideoStream(src=0).start()
                vs = VideoStream(usePiCamera=True).start()
                fileStream = False
                time.sleep(1.0)

                print("[INFO] video stream started...")

                drawImage(look_into_eyes_boi_pic)
                time.sleep(2)

                # loop over frames from the video stream
                while True:
                        
                        drawImage(pepe_give_wink_pic)


                        # if this is a file video stream, then we need to check if
                        # there any more frames left in the buffer to process
                        if fileStream and not vs.more():
                                break

                        # grab the frame from the threaded video file stream, resize
                        # it, and convert it to grayscale
                        # channels)
                        frame = vs.read()
                        frame = imutils.resize(frame, width=450)
                        # frame = imutils.rotate(frame, 180)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                        # detect faces in the grayscale frame
                        rects = detector(gray, 0)

                        # loop over the face detections
                        for rect in rects:
                                # determine the facial landmarks for the face region, then
                                # convert the facial landmark (x, y)-coordinates to a NumPy
                                # array
                                shape = predictor(gray, rect)
                                shape = face_utils.shape_to_np(shape)

                                # extract the left and right eye coordinates, then use the
                                # coordinates to compute the eye aspect ratio for both eyes
                                leftEye = shape[lStart:lEnd]
                                rightEye = shape[rStart:rEnd]
                                leftEAR = eye_aspect_ratio(leftEye)
                                rightEAR = eye_aspect_ratio(rightEye)

                                # # Use this for debugging with desktop screen attached
                                # compute the convex hull for the left and right eye, then
                                # visualize each of the eyes
                                # leftEyeHull = cv2.convexHull(leftEye)
                                # rightEyeHull = cv2.convexHull(rightEye)
                                # cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                                # cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                                # check to see if only one eye aspect ratio is below the blink 
                                # threshold, and if so, increment the blink frame counter (XOR)
                                if leftEAR < EYE_AR_THRESH != rightEAR < EYE_AR_THRESH :
                                        COUNTER += 1

                                # otherwise, the eye aspect ratio is not below the blink
                                # threshold
                                else:
                                        # if the eyes were closed for a sufficient number of
                                        # then increment the total number of blinks
                                        if COUNTER >= EYE_AR_CONSEC_FRAMES:
                                                TOTAL += 1
                                                os.system("mpg123 " + audioFile)
                                                showGIF(pepe_wink_gif, 1)
                                                
                                                

                                        # reset the eye frame counter
                                        COUNTER = 0

                                # draw the total number of blinks on the frame along with
                                # the computed eye aspect ratios for the frame
                                # cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                                #         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                # cv2.putText(frame, "LeftEAR: {:.2f}".format(leftEAR), (300, 30),
                                #         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                # cv2.putText(frame, "RightEAR: {:.2f}".format(rightEAR), (300, 60),
                                #         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                                # create strings for display
                                # BLINKS = "Blinks: {}".format(TOTAL)
                                # LEFTEAR = "LeftEAR: {:.2f}".format(leftEAR)
                                # RIGHTEAR = "RightEAR: {:.2f}".format(rightEAR)

                                # y = padding
                                # draw.text((x, y), BLINKS, font=font, fill="#FFFFFF")
                                # y += font.getsize(BLINKS)[1]
                                # draw.text((x, y), LEFTEAR, font=font, fill="#FFFF00")
                                # y += font.getsize(LEFTEAR)[1]
                                # draw.text((x, y), RIGHTEAR, font=font, fill="#FFFF00")

                                # # Display image.
                                # disp.image(image)
                                # time.sleep(0.1)

                        # print counts
                        print("Total winks: ", TOTAL)
                        # # Use this for debugging with desktop screen attached
                        # # show the frame on screen
                        # cv2.imshow("Frame", frame)
                        # key = cv2.waitKey(1) & 0xFF
                        # if the `q` key was pressed, break from the loop
                        # if key == ord("q"):
                        #         break

                        # break loop if switch is pulled back to normal mode
                        if switch.value == True:
                                print("go to normal mode")
                                drawImage(pepe_miss_you_pic)
                                time.sleep(2)
                                break


                # do a bit of cleanup
                print("[INFO] stopping video stream ...")
                cv2.destroyAllWindows()
                vs.stop()
        
        else:
                print("normal mode...")
                drawImage(msc_max_pic)
                if (time.time_ns() //1_000_000) - previousTime > interval:
                        previousTime = time.time_ns() // 1_000_000
                        drawImage(msc_max_pepe_pic)
                        time.sleep(0.4)

        
        time.sleep(0.5)
