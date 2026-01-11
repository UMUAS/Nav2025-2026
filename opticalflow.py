import numpy as np
import cv2 as cv

widths = [1080, 720, 480]
out_w = widths[2]

def rescale(frame):
    global out_w
    h, w = frame.shape[:2]
    ratio = (out_w/w)
    return cv.resize(frame, (out_w, int(h*ratio)))

def main():
    cv.namedWindow('Frame')

    # cv.createTrackbar('Threshold', 'Frame', 128, 255, lambda _: None)
    # cv.createTrackbar('Blur', 'Frame', 3, 7, lambda _: None)

    cap = cv.VideoCapture('vid/lawn_watering.mp4')

    ret, src0 = cap.read()
    frame0 = rescale(src0)

    prvs = cv.cvtColor(frame0, cv.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame0)
    hsv[..., 1] = 255

    while True:
        ret, src_frame = cap.read()
        if not ret:
            print('No frames grabbed!')
            break

        frame = rescale(src_frame)
        nxt = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(prvs, nxt, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang*180/np.pi/2
        hsv[..., 2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
        bgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        
        # thresh_val = cv.getTrackbarPos('Threshold', 'Frame')
        # blur_val = cv.getTrackbarPos('Blur', 'Frame')
    
        cv.imshow('Frame', frame)
        cv.imshow('Frame2', bgr)
        # cv.imshow('Frame2', frame_gray)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break

        prvs = nxt
    
    cv.destroyAllWindows()

if(__name__ == '__main__'):
    main()