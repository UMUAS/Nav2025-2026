#   receiver.py
#   Receive stereo depth stream from TCP connection.
#   
#   Press:
#       [q] - quit
#
#   Sends:
#       [timestamp:uint64]
#       [width:uint32]
#       [height:uint32]
#       [payload_size:uint32]
#       [png bytes]

import os
import sys
import socket
import struct
import time
import asyncio
import threading
from pathlib import Path

#import pymavlink
import cv2 as cv
import numpy as np

HOST = "100.89.62.208" #Raspberry Pi 4's Meshnet IP 
PORT = 5000

SAVE_DIR = Path("frames")
SAVE_DIR.mkdir(exist_ok=True)

def recv_exact(sock, n):
    """Receive exactly n bytes from a socket."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            # The connection was closed before receiving all bytes
            raise RuntimeError("Socket disconnected")
        data.extend(packet)
    return bytes(data)

def nothing(x):
    pass

win_name = 'frame_vis'

current_frame = None

def listen(sock):
    global running, current_frame

    while running:
        sock.sendall(b"GET_FRAME")

        header = sock.recv(20) # 8 + 3*4 = 20 bytes
        ts, w, h, size = struct.unpack("!QIII", header)

        data = recv_exact(sock, size)
        
        buf = np.frombuffer(data, dtype=np.uint8)

        depth = cv.imdecode(buf, cv.IMREAD_UNCHANGED)

        current_frame = depth

        filename = SAVE_DIR / f"received_{ts}.png"
        cv.imwrite(filename, depth)

        print("Saved! ", filename, f' ({len(data)/1000}kb, {os.path.getsize(filename)/1000}kb)')

        delay = cv.getTrackbarPos('Delay', 'menu')
        time.sleep(delay)

def display():
    global running, current_frame

    cv.namedWindow(win_name)

    cv.namedWindow('menu')
    cv.createTrackbar('Delay', 'menu', 0, 10, nothing)
    cv.setTrackbarMin('Delay', 'menu', 0)
    # cv.createTrackbar('Threshold Filter', 'menu', 255, 255, nothing)
    # cv.setTrackbarMin('Threshold Filter', 'menu', 0)

    while True:
        if current_frame is None:
            time.sleep(1)

        # thresh = cv.getTrackbarPos('Threshold Filter', 'menu')

        # _, masked = cv.threshold(current_frame, thresh, 255, cv.THRESH_TOZERO_INV) #TODO Doesnt work
        depth_vis = cv.normalize(current_frame, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)
        depth_vis = cv.applyColorMap(depth_vis,cv.COLORMAP_JET)

        cv.imshow(win_name, depth_vis)

        key = cv.waitKey(1)
        if key == ord('q'):
            running = False
            break

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Connecting to TCP server...')
sock.connect((HOST, PORT))
print('Connected!')

running = True

listener = threading.Thread(target=listen, args=(sock,))
listener.start()

displayer = threading.Thread(target=display)
displayer.start()

displayer.join()
# listener.join()

print('Exiting')
sock.close()
cv.destroyAllWindows()