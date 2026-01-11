import sys
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

# Load an image from file
a = cv.imread('img/flow2.webp')
# a = cv.imread('img/waterflow1.jpg')
src = cv.cvtColor(a, cv.COLOR_BGR2HSV)
img = src.copy()

# Check if the image loaded correctly
if src is None:
    sys.exit("Could not read the image.")

cv.namedWindow('Image Window')

# Create a trackbar for color change
# Arguments: trackbar name, window name, initial value, max value, callback function
cv.createTrackbar('Threshold', 'Image Window', 0, 255, lambda _: None)
cv.createTrackbar('Blur', 'Image Window', 3, 7, lambda _: None)

while(True):
    cv.imshow('Source', a)
    cv.imshow('Image Window', img)

    k = cv.waitKey(1) & 0xFF
    if k == 27: # Press 'ESC' to exit
        break

    thresh_val = cv.getTrackbarPos('Threshold', 'Image Window')
    blur_val = cv.getTrackbarPos('Blur', 'Image Window')

    blur = cv.blur(src, (blur_val, blur_val))
    _, img = cv.threshold(blur, thresh_val, 255, cv.THRESH_BINARY)

    hue_channel = cv.extractChannel(img, 0)
    sat_channel = cv.bitwise_not(cv.extractChannel(img, 1))
    value_channel = cv.extractChannel(img, 2)
    
    cont, _ = cv.findContours(value_channel, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    value_channel_rgb = cv.cvtColor(value_channel, cv.COLOR_GRAY2BGR)
    cv.drawContours(value_channel_rgb, cont, -1, (0, 255, 0), 3)

    sat_thinned = cv.ximgproc.thinning(sat_channel)
    val_thinned = cv.ximgproc.thinning(value_channel)

    cv.imshow('Hue', hue_channel)
    cv.imshow('Saturation', sat_channel)
    cv.imshow('Value', value_channel_rgb)
    cv.imshow('Saturation Skeleton', sat_thinned)
    cv.imshow('Value Skeleton', val_thinned)

cv.destroyAllWindows()