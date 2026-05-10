#   transmitter.py
#   Stream Stereo depth map from OAK-D camera over TCP
#
#   Sends:
#       [timestamp:uint64]
#       [width:uint32]
#       [height:uint32]
#       [payload_size:uint32]
#       [png bytes]

import socket
import struct
import time
import os

import cv2 as cv
import depthai as dai
import numpy as np

HOST = "0.0.0.0"
PORT = 5000

SAVE_DIR = "frames"
os.makedirs(SAVE_DIR, exist_ok=True)

# -- DepthAI Pipeline --
pipeline = dai.Pipeline()
leftCam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
rightCam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)
stereo = pipeline.create(dai.node.StereoDepth)

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.FAST_ACCURACY) # FAST_ACCURACY best for accuracy, but less detail

leftOut = leftCam.requestFullResolutionOutput()
rightOut = rightCam.requestFullResolutionOutput()

leftOut.link(stereo.left)
rightOut.link(stereo.right)

queue = stereo.depth.createOutputQueue()

# -- TCP Server --
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1) # Max one client at a time
print(f'Listening on {HOST}:{PORT}')

print('Opening DepthAI pipeline...')
pipeline.start()
try:
    # Server keeps waiting until connection accepted. When connection ends, keep waiting.
    while True:
        conn,addr = server.accept()
        print('Client connected: ', addr)

        try:
            while True:
                conn_data = conn.recv(1024)

                if not conn_data:
                    print('Client disconnected')
                    conn.close()
                    break

                cmd = conn_data.decode().strip()

                if cmd == 'GET_FRAME':
                    t = int(time.time()*1000) #Accurate to the millisecond

                    pipeline
                    frame = queue.get()
                    assert isinstance(frame, dai.ImgFrame)
                    
                    cvFrame = frame.getCvFrame()
                    h, w = cvFrame.shape

                    t1 = time.time()
                    _, encoded = cv.imencode('.png', cvFrame, [cv.IMWRITE_PNG_COMPRESSION, 5])
                    print(f'Encoding took {time.time()-t1:.4f}s')

                    cv.imwrite(f'{SAVE_DIR}/frame_{t}.png', encoded)
                    data = encoded.tobytes()
                    conn.sendall(struct.pack('!QIII', t, w, h, len(data)) + data)
        except ConnectionError as e:
            print(e, f' | Client {addr} may have disconnected.')
finally:
    pipeline.stop()
    print('OAK-D Pipeline closed!')

    server.close()
    print('TCP server closed!')