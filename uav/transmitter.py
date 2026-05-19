#   transmitter.py
#   Stream Stereo depth map from OAK-D camera over TCP
#   
#   Initial Send:
#       [hfov:float]
#
#   Frame Send:
#       [timestamp:uint64]
#       [depth payload size:uint32]
#       [color payload size:uint32]
#       [depth png bytes]
#       [color jpg bytes]

import socket
import struct
import time
from datetime import timedelta
import os
import json
from pathlib import Path
import argparse

import cv2 as cv
import depthai as dai
import numpy as np

# calib_modes = {
#     'on_start': dai.Pipeline.AutoCalibrationMode.ON_START,
#     'continuous': dai.Pipeline.AutoCalibrationMode.CONTINUOUS,
#     'off': dai.Pipeline.AutoCalibrationMode.OFF
# }

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-ip', default='0.0.0.0', help='Open socket on this IP address')
parser.add_argument('-port', type=int, default=5000, help='Open socket on this port')
parser.add_argument('-dir', default='frames', help='Save directory')
parser.add_argument('-nosave', action='store_true', help='Do not save frames in a folder')
parser.add_argument('-fps', default=10, type=int, help='FPS')
# parser.add_argument('-calib', '--calibration', choices=calib_modes.keys(), help='Specify mode for camera automatic calibration (CONTINUOUS best for accuracy)')

args = parser.parse_args()

ip = args.ip
port = args.port
save_dir = args.dir
no_save = args.nosave
fps = args.fps

# calib_mode = None
# if(args.calibration is not None):
    # calib_mode = calib_modes[args.calibration]

color_dir = os.path.join(save_dir,'color')
depth_dir = os.path.join(save_dir,'depth')
if(not no_save):
    os.makedirs(color_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)

# -- DepthAI Pipeline --
pipeline = dai.Pipeline()

# if calib_mode is not None:
    # pipeline.setAutoCalibrationMode(calib_mode)

camRgb = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
leftCam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
rightCam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)
stereo = pipeline.create(dai.node.StereoDepth)
sync = pipeline.create(dai.node.Sync)

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.FAST_ACCURACY) # FAST_ACCURACY best for accuracy, but less detail

sync.setSyncThreshold(timedelta(1/(2*fps)))

leftOut = leftCam.requestFullResolutionOutput(fps=fps)
rightOut = rightCam.requestFullResolutionOutput(fps=fps)
rgbOut = camRgb.requestOutput(size = (1280, 800), fps=fps, type=dai.ImgFrame.Type.NV12, enableUndistortion=True)

leftOut.link(stereo.left)
rightOut.link(stereo.right)
rgbOut.link(sync.inputs['rgb'])

stereo.depth.link(sync.inputs['depth_aligned'])
# stereo.setDepthAlign(dai.StereoDepthConfig.AlgorithmControl.DepthAlign.CENTER)
rgbOut.link(stereo.inputAlignTo)

queue = sync.out.createOutputQueue(maxSize=2)

IR_DOT_INTENSITY = 0.3
IR_FLOOD_INTENSITY = 0.1

ir_on = False

def updateIr(ir_on):
    if ir_on:
        pipeline.getDefaultDevice().setIrFloodLightIntensity(IR_FLOOD_INTENSITY)
        pipeline.getDefaultDevice().setIrLaserDotProjectorIntensity(IR_DOT_INTENSITY)
    else:
        pipeline.getDefaultDevice().setIrFloodLightIntensity(0)
        pipeline.getDefaultDevice().setIrLaserDotProjectorIntensity(0)

# -- TCP Server --
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen(1) # Max one client at a time
server.settimeout(10.0)
print(f'Listening on {ip}:{port}')

pipeline.start()
print('Opened DepthAI pipeline.')
try:
    updateIr(ir_on)
    
    HFOV = np.deg2rad(pipeline.getDefaultDevice().getCalibration().getFov(dai.CameraBoardSocket.CAM_B))

    with open(os.path.join(save_dir,'metadata.json'), 'w') as f:
        json.dump(HFOV, f)

    # Server keeps waiting until connection accepted. When connection ends, keep waiting.
    while True:
        try:
            conn,addr = server.accept()
        except socket.timeout:
            continue

        print('Client connected: ', addr)

        try:
            conn.sendall(struct.pack('!d', HFOV)) # important for depth calculation!

            while True:
                conn_data = conn.recv(1024)

                if not conn_data:
                    print('Client disconnected')
                    conn.close()
                    break

                cmd = conn_data.decode().strip()

                if cmd == 'GET_FRAME' or cmd == 'GET_FRAME_HQ':
                    hq = cmd == 'GET_FRAME_HQ'
                    t = int(time.time()*1000) #Accurate to the millisecond

                    messageGroup = queue.get()
                    assert isinstance(messageGroup, dai.MessageGroup)
                    color = messageGroup["rgb"]
                    assert isinstance(color, dai.ImgFrame)
                    depth = messageGroup["depth_aligned"]
                    assert isinstance(depth, dai.ImgFrame)
                    
                    cvColor = color.getCvFrame()
                    cvDepth = depth.getCvFrame()

                    if(not hq):
                        cvDepth = cv.resize(cvDepth, (640, 400))
                        cvColor = cv.resize(cvColor, (640, 400))

                    t1 = time.time()
                    _, encoded_depth = cv.imencode('.png', cvDepth, [cv.IMWRITE_PNG_COMPRESSION, 5]) #High compression but slow
                    if(hq):
                        _, encoded_color = cv.imencode('.jpg', cvColor, [cv.IMWRITE_JPEG_QUALITY, 80]) #High quality
                    else:
                        _, encoded_color = cv.imencode('.jpg', cvColor, [cv.IMWRITE_JPEG_QUALITY, 10]) #Low quality for streaming (1-100)
                    print(f'Encoding took {time.time()-t1:.4f}s')

                    if not no_save:
                        with open(Path(f'{save_dir}/depth/depth_{t}.png'), 'wb') as f:
                            f.write(encoded_depth.tobytes())

                        with open(Path(f'{save_dir}/color/color_{t}.jpg'), 'wb') as f:
                            f.write(encoded_color.tobytes())
                    
                    depth_data = encoded_depth.tobytes()
                    color_data = encoded_color.tobytes()
                    conn.sendall(struct.pack('!QII', t, len(depth_data), len(color_data)) + depth_data + color_data)
                elif cmd == 'TOGGLE_IR':
                    ir_on = not ir_on
                    print(f'Toggling {'on' if ir_on else 'off'} IR projectors.')
                    updateIr(ir_on)

        except ConnectionError as e:
            print(e, f' | Client {addr} may have disconnected.')
except KeyboardInterrupt:
    print('Keyboard interrupt')
finally:
    pipeline.stop()
    print('OAK-D Pipeline closed!')

    server.close()
    print('TCP server closed!')