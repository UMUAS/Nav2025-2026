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

    cv.createTrackbar('Max. Sat', 'Frame', 80, 255, lambda _: None)
    cv.createTrackbar('Min. Val', 'Frame', 140, 255, lambda _: None)
    # cv.createTrackbar('Blur', 'Frame', 3, 7, lambda _: None)

    cap = cv.VideoCapture('vid/lawn_watering.mp4')
    # cap = cv.VideoCapture('vid/sprinkler.mp4')
    # cap = cv.VideoCapture('vid/apt_fire.mp4')

    ret, src0 = cap.read()
    frame0 = rescale(src0)

    prvs = cv.cvtColor(frame0, cv.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame0)
    hsv[..., 1] = 255

    while True:
        ret, src_frame = cap.read()
        if not ret:
            cap.set(cv.CAP_PROP_POS_FRAMES, 0)
            continue
            # print('No frames grabbed!')
            # break

        frame = rescale(src_frame)

        nxt = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(prvs, nxt, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang*180/np.pi/2
        hsv[..., 2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
        bgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        
        minval_val = cv.getTrackbarPos('Min. Val', 'Frame')
        maxsat_val = cv.getTrackbarPos('Max. Sat', 'Frame')
        # blur_val = cv.getTrackbarPos('Blur', 'Frame')

        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        _, sat = cv.threshold(cv.extractChannel(frame_hsv, 1), maxsat_val, 255, cv.THRESH_BINARY_INV)
        _, val = cv.threshold(cv.extractChannel(frame_hsv, 2), minval_val, 255, cv.THRESH_BINARY)

        comb = cv.bitwise_and(sat, val)
        
        masked_bgr = cv.bitwise_and(bgr, bgr, mask=comb)

        # modif = thresh
    
        cv.imshow('Frame', frame)
        cv.imshow('Value', val)
        cv.imshow('Saturation', sat)
        cv.imshow('Value+Satruation', comb)
        cv.imshow('Optical Flow', bgr)
        cv.imshow('Masked Optical Flow', masked_bgr)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv.imwrite('results/frame.png', frame)
            cv.imwrite('results/hsv_value.png', val)
            cv.imwrite('results/hsv_saturation.png', sat)
            cv.imwrite('results/value_satruation_blend.png', comb)
            cv.imwrite('results/optical_flow.png', bgr)
            cv.imwrite('results/masked_optical_flow.png', masked_bgr)

        prvs = nxt
    
    cv.destroyAllWindows()

if(__name__ == '__main__'):
    main()