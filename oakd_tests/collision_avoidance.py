#!/usr/bin/env python3

import depthai as dai
import cv2
import numpy as np
import math

# User-defined constants
WARNING = 2000  # 200cm, orange
CRITICAL = 500  # 50cm, red

FPS = 15

# Create pipeline
pipeline = dai.Pipeline()

# Color camera
camRgb = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
# camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
# camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
# color_output = camRgb.requestOutput((1280,720), type=dai.ImgFrame.Type.RGB888p)
color_output = camRgb.requestOutput((1280, 720), type=dai.ImgFrame.Type.NV12, fps=FPS)
# color_output = camRgb.requestFullResolutionOutput(type=dai.ImgFrame.Type.NV12)

# Define source - stereo depth cameras
left = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
left_output = left.requestOutput((640, 400), type=dai.ImgFrame.Type.NV12, fps=FPS)
# left_output = left.requestFullResolutionOutput(dai.ImgFrame.Type.NV12)

right = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)
right_output = right.requestOutput((640, 400), type=dai.ImgFrame.Type.NV12, fps=FPS)
# right_output = right.requestFullResolutionOutput(dai.ImgFrame.Type.NV12)

# Create stereo depth node
stereo = pipeline.create(dai.node.StereoDepth).build(left=left_output, right=right_output)
stereo.initialConfig.setConfidenceThreshold(50)
stereo.setLeftRightCheck(True)
stereo.setExtendedDisparity(True)

# Spatial location calculator configuration
slc = pipeline.create(dai.node.SpatialLocationCalculator)
for x in range(15):
    for y in range(9):
        config = dai.SpatialLocationCalculatorConfigData()
        config.depthThresholds.lowerThreshold = 200
        config.depthThresholds.upperThreshold = 10000
        config.roi = dai.Rect(dai.Point2f((x+0.5)*0.0625, (y+0.5)*0.1), dai.Point2f((x+1.5)*0.0625, (y+1.5)*0.1))
        config.calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
        slc.initialConfig.addROI(config)

stereo.depth.link(slc.inputDepth)
color_output.link(stereo.inputAlignTo)

# Syncinc
sync = pipeline.create(dai.node.Sync)
sync.setRunOnHost(True)
color_output.link(sync.inputs['color'])
slc.out.link(sync.inputs['slc'])

outputQueue = sync.out.createOutputQueue()
pipeline.start()

# Connect to device and start pipeline
with pipeline:
    while pipeline.isRunning():
        # Output queues will be used to get the color mono frames and spatial location data
        fontType = cv2.FONT_HERSHEY_TRIPLEX

        msgGroup : dai.MessageGroup = outputQueue.get()
        inColor = msgGroup['color']
        inSlc = msgGroup['slc']
        # inColor = qColor.get()  # Try to get a frame from the color camera
        # inSlc = qSlc.get()  # Try to get spatial location data

        if inColor is None:
            print("No color camera data")
        if inSlc is None:
            print("No spatial location data")

        colorFrame = None
        if inColor is not None:
            colorFrame = inColor.getCvFrame()  # Fetch the frame from the color mono camera

        if inSlc is not None and colorFrame is not None:
            slc_data = inSlc.getSpatialLocations()
            for depthData in slc_data:
                roi = depthData.config.roi
                roi = roi.denormalize(width=colorFrame.shape[1], height=colorFrame.shape[0])

                xmin = int(roi.topLeft().x)
                ymin = int(roi.topLeft().y)
                xmax = int(roi.bottomRight().x)
                ymax = int(roi.bottomRight().y)

                coords = depthData.spatialCoordinates
                distance = math.sqrt(coords.x ** 2 + coords.y ** 2 + coords.z ** 2)

                if distance == 0:  # Invalid
                    continue

                # Determine color based on distance
                if distance < CRITICAL:
                    color = (0, 0, 255)  # Red
                elif distance < WARNING:
                    color = (0, 140, 255)  # Orange
                else:
                    continue  # Skip drawing for non-critical/non-warning distances

                # Draw rectangle and distance text on the color frame
                cv2.rectangle(colorFrame, (xmin, ymin), (xmax, ymax), color, thickness=2)
                cv2.putText(colorFrame, "{:.1f}m".format(distance / 1000), (xmin + 10, ymin + 20), fontType, 0.5, color)

            # Display the color frame
            cv2.imshow('Left Mono Camera', colorFrame)
            if cv2.waitKey(1) == ord('q'):
                break
