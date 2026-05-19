import os
import glob
import json

import math
import cv2 as cv
import numpy as np
import argparse

from rich.console import Console
from rich.panel import Panel

from utils import gcs_utils

parser = argparse.ArgumentParser(description='View depth frames and measure relative distances between physical points')
parser.add_argument('--path', default='frames', type=str, help='Directory to folder with depth frames')
args = parser.parse_args()

path = args.path
depth_files = glob.glob(os.path.join(path, 'depth', 'depth_*.png'))
color_files = glob.glob(os.path.join(path, 'color', 'color_*.jpg'))
if not depth_files:
    print("No images found.")
    exit()

def nothing(x):
    pass

console = Console()
console.set_window_title('Depth Viewer & Measurer')

title = "[bold magenta]Depth Viewer & Measurer[/bold magenta]"
description = (
    "View depth frames and measure relative distances between physical points.\n"
    "[yellow]Click 2 points to measure their distance in [bold]millimeters[/bold][yellow]"
)

console.print(Panel.fit(f"{title}\n\n{description}",border_style="blue"))
console.print("\n[bold yellow]Inputs:[/bold yellow]")
console.print(f"\t[red]\\[q] = Quit.[/red]")
console.print(f"\t\\[r] = Refresh folder.")
console.print(f"\t\\[a] = Decrement index.")
console.print(f"\t\\[d] = Increment index.")
console.print(f"\t\\[t] = Toggle between showing depth/color only.")

size = len(depth_files)

def on_change_index(x):
    global depth, color

    depth = cv.imread(depth_files[index], cv.IMREAD_UNCHANGED)
    color = None
    if index < len(color_files) and color_files[index] is not None:
        color = cv.imread(color_files[index], cv.IMREAD_UNCHANGED)

# OpenCV window
WIN_NAME = 'Image Slider'
cv.namedWindow(WIN_NAME, cv.WINDOW_NORMAL)
cv.createTrackbar('Index', WIN_NAME, 0, size - 1, on_change_index)
cv.createTrackbar('Max. depth (cm)', WIN_NAME, 3000, 3000, nothing)
cv.setTrackbarMin('Max. depth (cm)', WIN_NAME, 1)
# cv.createTrackbar('Min. depth (mm)', win_name, 1, 1000, nothing)
# cv.setsTrackbarMin('Min. depth (mm)', win_name, 1)
cv.createTrackbar('Speckle Size', WIN_NAME, 48, 255, nothing)
cv.setTrackbarMin('Speckle Size', WIN_NAME, 0)
cv.createTrackbar('Speckle Difference', WIN_NAME, 200, 255, nothing)
cv.setTrackbarMin('Speckle Difference', WIN_NAME, 0)
cv.createTrackbar('Depth Overlay %', WIN_NAME, 60, 100, nothing)

depth = cv.imread(depth_files[0], cv.IMREAD_UNCHANGED)
color = None
if color_files[0] is not None:
    color = cv.imread(color_files[0], cv.IMREAD_COLOR)

try:
    with open(os.path.join(path, 'metadata.json'), 'r') as f:
        HFOV = json.load(f)
except FileNotFoundError:
    print('Missing metadata.json!')
except TypeError:
    print('Error while parsing values from metdata.json!')

points = []

def depth_to_spatial(dist, x, y):
    global HFOV
    return (
        dist*math.tan(HFOV / 2.0) * (x-depth.shape[1]/2) / (depth.shape[1] / 2.0),
        -dist*math.tan(HFOV / 2.0) * (y-depth.shape[0]/2) / (depth.shape[1] / 2.0),
        dist) #X,Y,Z

current_message = 'Click a point to measure'
current_reading = ''

def clickEvent(event, x,y, flags, param):
    global points, depth, current_message, current_reading

    if depth is None:
        return
    
    index = -1

    if event == cv.EVENT_LBUTTONDOWN:
        index = 0
    elif event == cv.EVENT_RBUTTONDOWN:
        index = 1
    
    if index == -1:
        return

    if len(points) >= 2:
        points.pop(index)
    
    points.insert(index, (x, y))

    x1, y1 = points[0]

    d1 = depth[y1, x1]
    z1 = float(d1)/10.0 #mm to cm

    current_d = depth[points[index][1], points[index][0]]
    current_z = float(current_d)/10.0

    current_reading = f'Depth: {current_z:.2f} cm'

    if len(points) == 1:
        current_message = 'Click another point to measure distance'
        # print('Click another point to measure distance.')
        console.print(f'[yellow]{current_message}[/yellow]')
        return

    x2, y2 = points[1]

    d2 = depth[y2, x2]
    z2 = float(d2)/10.0 #mm to cm

    if z1 == 0 or z2 == 0:
        current_reading = ''
        if z1 == z2:
            current_message = f'[red]Depth undefined at points!'
        elif z1 == 0:
            current_message = f'[red]Depth undefined at point 1!'
        else:
            current_message = f'[red]Depth undefined at point 2!'
        
        console.print(f'[red]{current_message}[/red]')
        return

    X1, Y1, _ = depth_to_spatial(z1, x1, y1)
    X2, Y2, _ = depth_to_spatial(z2, x2, y2)

    dist_cm = np.sqrt((X2-X1)**2 + (Y2-Y1)**2 + (z2-z1)**2)

    console.print(f'Depth 1: {z1} cm @\\[x:{x1},y:{y1}]px')
    console.print(f'Depth 2: {z2} cm @\\[x:{x2},y:{y2}]px')
    console.print(f'[green]-> Relative distance: [bold]{dist_cm:.2f} cm[/bold][/green]')
    current_message = f'Points {dist_cm:.2f} cm apart!'

cv.setMouseCallback(WIN_NAME, clickEvent)

while True:
    index = cv.getTrackbarPos('Index', WIN_NAME)

    maxSpeckleSize = cv.getTrackbarPos('Speckle Size', WIN_NAME)
    maxSpeckleDiff = cv.getTrackbarPos('Speckle Difference', WIN_NAME)
    maxDepth = cv.getTrackbarPos('Max. depth (cm)', WIN_NAME)*10 #to mm
    depthBlend = cv.getTrackbarPos('Depth Overlay %', WIN_NAME)/100.0
    minDepth_mm = 1

    key = cv.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('d'):
        #Increment index
        index = min(index+1, size-1)
        cv.setTrackbarPos('Index', WIN_NAME, index)
        points = []
    elif key == ord('a'):
        #Decrement index
        index = max(index-1, 0)
        cv.setTrackbarPos('Index', WIN_NAME, index)
        points = []
    elif key == ord('r'):
        print('Refreshing folder')
        #Refresh folder
        depth_files = glob.glob(os.path.join(path, 'depth', 'depth_*.png'))
        color_files = glob.glob(os.path.join(path, 'color', 'color_*.png'))
        size = len(depth_files)
        if not depth_files:
            print("No images found.")
            exit()
        
        cv.setTrackbarMax('Index', WIN_NAME, size-1)
        index = max(min(size-1, index),0)
        cv.setTrackbarPos(index)
    elif key == ord('t'):
        if (depthBlend == 1.0):
            cv.setTrackbarPos('Depth Overlay %', WIN_NAME, 0)
        else:
            cv.setTrackbarPos('Depth Overlay %', WIN_NAME, 100)

    if depth is None:
        continue

    disp = gcs_utils.visualize(depth, color, maxSpeckleSize, maxSpeckleDiff, maxDepth, depthBlend)

    if(len(points) > 0):
        x,y = points[0]
        disp = cv.drawMarker(disp, (x,y), (255, 0, 0), cv.MARKER_CROSS, 20, 1, cv.LINE_AA)
        cv.putText(disp, '1', (x-10,y-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)
    if(len(points) > 1):
        x,y = points[1]
        disp = cv.drawMarker(disp, (x,y), (0, 255, 0), cv.MARKER_CROSS, 20, 1, cv.LINE_AA)
        cv.putText(disp, '2', (x-10,y-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)

    if len(points) == 2:
        disp = cv.line(disp, pt1=points[0], pt2=points[1], color=(0,0,255), thickness=1, lineType=cv.LINE_AA)
    
    if(current_message.startswith('[red]')):
        cv.putText(disp, current_message[5:], (20, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 3, cv.LINE_AA) #Outline
        cv.putText(disp, current_message[5:], (20, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv.LINE_AA)
    else:
        cv.putText(disp, current_message, (20, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 3, cv.LINE_AA) #Outline
        cv.putText(disp, current_message, (20, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv.LINE_AA)
    
    cv.putText(disp, current_reading, (int(disp.shape[1])-len(current_reading)*15, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 3, cv.LINE_AA) #Outline
    cv.putText(disp, current_reading, (int(disp.shape[1])-len(current_reading)*15, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv.LINE_AA)

    cv.imshow(WIN_NAME, disp)
    cv.setWindowTitle(WIN_NAME, depth_files[index]) # Shows file name of current image
        
cv.destroyAllWindows()