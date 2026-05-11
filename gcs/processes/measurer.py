import os
import glob
import json

import math
import cv2 as cv
import numpy as np
import argparse

from rich.console import Console
from rich.panel import Panel

parser = argparse.ArgumentParser(description='View depth frames and measure relative distances between physical points')
parser.add_argument('--path', default='frames', type=str, help='Directory to folder with depth frames')
args = parser.parse_args()

path = args.path
image_files = glob.glob(os.path.join(path, '*.png'))
if not image_files:
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

# Title + description panel
console.print(Panel.fit(f"{title}\n\n{description}",border_style="blue"))

console.print("\n[bold yellow]Inputs:[/bold yellow]")
console.print(f"\t[red]\\[q] = Quit.[/red]")
console.print(f"\t\\[r] = Refresh folder.")
console.print(f"\t\\[a] = Decrement index.")
console.print(f"\t\\[d] = Increment index.")

size = len(image_files)

# OpenCV window
win_name = 'Image Slider'
cv.namedWindow(win_name)
cv.createTrackbar('Index', win_name, 0, size - 1, nothing)

current_depth = None

try:
    with open(os.path.join(path, 'metadata.json'), 'r') as f:
        HFOV = json.load(f)
except FileNotFoundError:
    print('Missing metadata.json!')
except TypeError:
    print('Error while parsing values from metdata.json!')

points = []

def depth_to_spatial(depth, x, y):
    global current_depth, HFOV
    return (
        depth*math.tan(HFOV / 2.0) * (x-current_depth.shape[1]/2) / (current_depth.shape[1] / 2.0),
        -depth*math.tan(HFOV / 2.0) * (y-current_depth.shape[0]/2) / (current_depth.shape[1] / 2.0),
        depth) #X,Y,Z

def clickEvent(event, x,y, flags, param):
    global points, current_depth

    if current_depth is None:
        return
    
    if event == cv.EVENT_LBUTTONDOWN:
        if len(points) >= 2:
            points.pop(0)
        
        points.append((x, y))

        if len(points) == 1:
            print('Click another point to measure distance.')
            return

        (x1, y1), (x2, y2) = points

        d1 = current_depth[y1, x1]
        d2 = current_depth[y2, x2]

        z1 = float(d1)/10.0 #mm to cm
        z2 = float(d2)/10.0 #mm to cm

        if z1 is None or z2 is None:
            print('Depth undefined at point!')
            return

        X1, Y1, Z1 = depth_to_spatial(z1, x1, y1)
        X2, Y2, Z2 = depth_to_spatial(z2, x2, y2)

        dist_cm = np.sqrt((X2-X1)**2 + (Y2-Y1)**2 + (z2-z1)**2)

        print(f'Depth1: {z1} cm @ pixel: (x:{x1},y:{y1})')
        print(f'Depth2: {z2} cm @ pixel: (x:{x2},y:{y2})')
        print(f'-> Relative distance: {dist_cm} cm ({dist_cm/100:.2f} m)')

cv.setMouseCallback(win_name, clickEvent)

while True:
    index = cv.getTrackbarPos('Index', win_name)
    
    depth = cv.imread(image_files[index], cv.IMREAD_UNCHANGED)
    current_depth = depth

    if depth is not None:
        img = cv.cvtColor(depth, cv.COLOR_GRAY2BGR)
        depth_vis = cv.normalize(img, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)
        depth_vis = cv.applyColorMap(depth_vis,cv.COLORMAP_JET)

        for p in points:
            depth_vis = cv.circle(depth_vis, p, 5, (0, 0, 255), 1)
        
        if len(points) == 2:
            depth_vis = cv.line(depth_vis, pt1=points[0], pt2=points[1], color=(0,0,255), thickness=1)

        cv.imshow(win_name, depth_vis)
        cv.setWindowTitle(win_name, image_files[index]) # Shows file name of current image
    
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('d'):
        #Increment index
        index = min(index+1, size-1)
        cv.setTrackbarPos('Index', win_name, index)
        points = []
    elif key == ord('a'):
        #Decrement index
        index = max(index-1, 0)
        cv.setTrackbarPos('Index', win_name, index)
        points = []
    elif key == ord('r'):
        #Refresh folder
        image_files = glob.glob(os.path.join(path, '*.png'))
        size = len(image_files)
        if not image_files:
            print("No images found.")
            exit()
        
cv.destroyAllWindows()