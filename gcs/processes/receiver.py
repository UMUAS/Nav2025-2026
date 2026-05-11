#   receiver.py
#   Receive stereo depth stream from TCP connection.
#   
#   Press:
#       [q] - quit
#       [s] - Request frames switch (on/off)
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
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

#import pymavlink
import cv2 as cv
import numpy as np

HOST = "100.89.62.208" #Raspberry Pi 4's Meshnet IP 
PORT = 5000

console = Console()
console.set_window_title('Depth Frames Receiver')

title = "[bold magenta]Depth Frames Receiver[/bold magenta]"
description = (
    "Receive depth frames from TCP server and save them locally.\n"
)

# Title + description panel
console.print(Panel.fit(f"{title}\n\n{description}",border_style="blue"))

console.print("\n[bold yellow]Inputs:[/bold yellow]")
console.print(f"\t[red]\\[q] = Quit.[/red]")
console.print(f"\t\\[s] = Request frames switch (on/off).")

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
current_filename = None
req_auto = False

def listen(sock:socket.socket):
    global running, current_frame, current_filename, req_auto

    initial_bytes = sock.recv(8)
    HFOV = struct.unpack('!d', initial_bytes)[0]

    with open(SAVE_DIR / 'metadata.json', 'w') as f:
        json.dump(HFOV, f)

    while running:
        if not req_auto:
            continue
        sock.sendall(b"GET_FRAME")

        header = sock.recv(12) # 8 + 4 = 12 bytes
        ts, size = struct.unpack("!QI", header)

        data = recv_exact(sock, size)
        
        buf = np.frombuffer(data, dtype=np.uint8)

        depth = cv.imdecode(buf, cv.IMREAD_UNCHANGED)

        current_frame = depth

        filename = SAVE_DIR / f"received_{ts}.png"
        cv.imwrite(filename, depth)
        current_filename = filename

        print("Saved! ", filename, f' ({len(data)/1000:.0f} kb)')

        delay = cv.getTrackbarPos('Delay (s)', 'menu')
        time.sleep(delay)

def display():
    global running, current_frame, current_filename, req_auto

    cv.namedWindow(win_name)

    cv.namedWindow('menu')
    cv.createTrackbar('Delay (s)', 'menu', 0, 10, nothing)
    cv.setTrackbarMin('Delay (s)', 'menu', 0)

    while True:
        key = cv.waitKey(1)
        if key == ord('q'):
            running = False
            break
        if key == ord('s'):
            req_auto = not req_auto
            console.print('Requesting frames: ', '[green]on[/green]' if req_auto else '[red]off[/red]')

        if current_frame is None:
            # time.sleep(1)
            continue

        if current_filename is not None:
            cv.setWindowTitle(win_name, str(current_filename))

        depth_vis = cv.normalize(current_frame, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)
        depth_vis = cv.applyColorMap(depth_vis,cv.COLORMAP_JET)

        cv.imshow(win_name, depth_vis)

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
running = False
listener.join()

print('Exiting')
sock.close()
cv.destroyAllWindows()