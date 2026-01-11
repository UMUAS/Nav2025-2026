import numpy as np
import cv2 as cv

cap = cv.VideoCapture('vid/lawn_watering.mp4')

out_w = 1080
c = 1

def rescale(frame):
    global out_w
    h, w = frame.shape[:2]
    ratio = (out_w/w)
    return cv.resize(frame, (out_w, int(h*ratio)))
 
# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100, qualityLevel = 0.3, minDistance = 7, blockSize = 7 )
 
# Parameters for lucas kanade optical flow
lk_params = dict(winSize  = (15, 15), maxLevel = 2, criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

# Create some random colors
color = np.random.randint(0, 255, (100, 3))
 
# Take first frame and find corners in it
ret, src_frame = cap.read()
old_frame = rescale(src_frame)
old_gray = cv.extractChannel(cv.cvtColor(old_frame, cv.COLOR_BGR2HSV), 2)
p0 = cv.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
 
# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)

cv.namedWindow('Frame')

cv.createTrackbar('Threshold', 'Frame', 128, 255, lambda _: None)
cv.createTrackbar('Blur', 'Frame', 3, 7, lambda _: None)
 
while(1):
    ret, src_frame = cap.read()
    if not ret:
        print('No frames grabbed!')
        break

    frame = rescale(src_frame)
 
    # frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.extractChannel(cv.cvtColor(frame, cv.COLOR_BGR2HSV), 2)

    thresh_val = cv.getTrackbarPos('Threshold', 'Frame')
    blur_val = cv.getTrackbarPos('Blur', 'Frame')

    blur = cv.blur(frame_gray, (blur_val, blur_val))
    _, modif = cv.threshold(blur, thresh_val, 255, cv.THRESH_BINARY)
 
    # calculate optical flow
    p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, modif, p0, None, **lk_params)
 
    # Select good points
    if p1 is not None:
        good_new = p1[st==1]
        good_old = p0[st==1]
 
    # draw the tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv.line(mask, (int(a), int(b)), (int(c), int(d)), color[i].tolist(), 2)
        frame = cv.circle(frame, (int(a), int(b)), 5, color[i].tolist(), -1)
    img = cv.add(frame, mask)
 
    cv.imshow('Frame', img)
    cv.imshow('Frame2', modif)
    k = cv.waitKey(30) & 0xff
    if k == 27:
        break
 
    # Now update the previous frame and previous points
    # old_gray = frame_gray.copy()
    old_gray = modif.copy()
    p0 = good_new.reshape(-1, 1, 2)
 
cv.destroyAllWindows()