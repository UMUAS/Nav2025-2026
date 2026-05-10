import os
import glob

import cv2 as cv
import argparse

from rich.prompt import Prompt
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
console.print(f"\t[red]\[q] = Quit.[/red]")
console.print(f"\t\[r] = Refresh folder.")
console.print(f"\t\[a] = Decrement index.")
console.print(f"\t\[d] = Increment index.")

size = len(image_files)

# OpenCV window
win_name = 'Image Slider'
cv.namedWindow(win_name)
cv.createTrackbar('Index', win_name, 0, size - 1, nothing)

while True:
    index = cv.getTrackbarPos('Index', win_name)
    
    img = cv.imread(image_files[index])
    if img is not None:
        cv.imshow(win_name, img)
        cv.setWindowTitle(win_name, image_files[index]) # Shows file name of current image
    
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('d'):
        #Increment index
        index = min(index+1, size-1)
        cv.setTrackbarPos('Index', win_name, index)
    elif key == ord('a'):
        #Decrement index
        index = max(index-1, 0)
        cv.setTrackbarPos('Index', win_name, index)
    elif key == ord('r'):
        #Refresh folder
        image_files = glob.glob(os.path.join(path, '*.png'))
        size = len(image_files)
        if not image_files:
            print("No images found.")
            exit()
        
cv.destroyAllWindows()