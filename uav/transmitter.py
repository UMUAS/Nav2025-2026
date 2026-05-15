#   transmitter.py
#   Stream Stereo depth map from OAK-D camera over TCP
#   
#   Initial Send:
#       [focal_length_x:float]
#       [focal_length_y:float]
#       [principal_point_x:float]
#       [principal_point_y:float]
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
from datetime import timedelta
import os
import json

import cv2 as cv
import depthai as dai
import numpy as np

HOST = "0.0.0.0"
PORT = 5000

SAVE_DIR = "frames"
os.makedirs(SAVE_DIR, exist_ok=True)

FPS = 10

# -- DepthAI Pipeline --
pipeline = dai.Pipeline()
camRgb = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
leftCam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
rightCam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)
stereo = pipeline.create(dai.node.StereoDepth)
sync = pipeline.create(dai.node.Sync)

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.FAST_ACCURACY) # FAST_ACCURACY best for accuracy, but less detail

sync.setSyncThreshold(timedelta(1/(2*FPS)))

leftOut = leftCam.requestFullResolutionOutput(fps=FPS)
rightOut = rightCam.requestFullResolutionOutput(fps=FPS)
rgbOut = camRgb.requestOutput(size = (640, 400), fps=FPS, enableUndistortion=True)

leftOut.link(stereo.left)
rightOut.link(stereo.right)
rgbOut.link(sync.inputs['rgb'])

stereo.depth.link(sync.inputs['depth_aligned'])
rgbOut.link(stereo.inputAlignTo)

# queue = stereo.depth.createOutputQueue()
queue = sync.out.createOutputQueue()

# -- TCP Server --
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1) # Max one client at a time
print(f'Listening on {HOST}:{PORT}')

pipeline.start()
print('Opened DepthAI pipeline.')
try:
    HFOV = np.deg2rad(pipeline.getDefaultDevice().getCalibration().getFov(dai.CameraBoardSocket.CAM_B))

    with open(os.path.join(SAVE_DIR,'metadata.json'), 'w') as f:
        # json.dump((baseline_cm,fx,fy,cx,cy), f)
        json.dump(HFOV, f)

    # Server keeps waiting until connection accepted. When connection ends, keep waiting.
    while True:
        print('Waiting for connection...')
        conn,addr = server.accept()
        print('Client connected: ', addr)

        try:
            print('Sending camera intrinsics first')
            # conn.sendall(struct.pack('!fffff', baseline_cm, fx, fy, cx, cy))
            conn.sendall(struct.pack('!d', HFOV))

            while True:
                conn_data = conn.recv(1024)

                if not conn_data:
                    print('Client disconnected')
                    conn.close()
                    break

                cmd = conn_data.decode().strip()

                if cmd == 'GET_FRAME':
                    t = int(time.time()*1000) #Accurate to the millisecond

                    messageGroup = queue.get()
                    assert isinstance(messageGroup, dai.MessageGroup)
                    color = messageGroup["rgb"]
                    assert isinstance(color, dai.ImgFrame)
                    depth = messageGroup["depth_aligned"]
                    assert isinstance(depth, dai.ImgFrame)
                    
                    cvColor = color.getCvFrame()
                    cvDepth = depth.getCvFrame()

                    t1 = time.time()
                    _, encoded_depth = cv.imencode('.png', cvDepth, [cv.IMWRITE_PNG_COMPRESSION, 6]) #High compression but slow
                    _, encoded_color = cv.imencode('.jpg', cvColor, [cv.IMWRITE_JPEG_QUALITY, 10]) #Low quality for streaming (1-100)
                    print(f'Encoding took {time.time()-t1:.4f}s')

                    cv.imwrite(f'{SAVE_DIR}/depth_{t}.png', encoded_depth)
                    cv.imwrite(f'{SAVE_DIR}/color_{t}.jpg', encoded_color)
                    depth_data = encoded_depth.tobytes()
                    color_data = encoded_color.tobytes()
                    conn.sendall(struct.pack('!QII', t, len(depth_data), len(color_data)) + depth_data + color_data)
        except ConnectionError as e:
            print(e, f' | Client {addr} may have disconnected.')
except KeyboardInterrupt:
    print('Keyboard interrupt')
finally:
    pipeline.stop()
    print('OAK-D Pipeline closed!')

    server.close()
    print('TCP server closed!')