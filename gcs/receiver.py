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
import queue
import threading
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

#import pymavlink
import cv2 as cv
import numpy as np

from utils import gcs_utils

HOST = "100.89.62.208" #Raspberry Pi 4's Meshnet IP 
PORT = 5000

console = Console()

WIN_NAME = 'frame_vis'

SAVE_DIR = Path("frames")
(SAVE_DIR / 'depth').mkdir(parents=True, exist_ok=True)
Path(SAVE_DIR / 'color').mkdir(exist_ok=True)

current_depth = None
current_color = None
current_ts = None

req_auto = False
running = True

save_queue = queue.Queue()

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

def getFrame(sock:socket.socket):
    sock.sendall(b"GET_FRAME")

    header = sock.recv(16) # 8 + 4 + 4 = 16 bytes
    ts, depth_size, color_size = struct.unpack("!QII", header)

    depth_data = recv_exact(sock, depth_size)
    color_data = recv_exact(sock, color_size)
    
    d_buf = np.frombuffer(depth_data, dtype=np.uint8)
    c_buf = np.frombuffer(color_data, dtype=np.uint8)

    depth = cv.imdecode(d_buf, cv.IMREAD_UNCHANGED)
    color = cv.imdecode(c_buf, cv.IMREAD_COLOR)

    return (ts, depth, color) 

def listen(sock:socket.socket):
    global running, current_depth, current_color, current_ts, req_auto

    try:
        initial_bytes = sock.recv(8)
        HFOV = struct.unpack('!d', initial_bytes)[0]

        with open(SAVE_DIR / 'metadata.json', 'w') as f:
            json.dump(HFOV, f)

        while running:
            if not req_auto:
                continue
            
            data = getFrame(sock)
            
            current_ts = data[0]
            current_depth = data[1]
            current_color = data[2]
            
            save_queue.put(data)

            delay = cv.getTrackbarPos('Delay (s)', WIN_NAME)
            time.sleep(delay)
    except Exception as e:
        console.print(f"[red]Listener error:[/red] {e}")
    finally:
        running = False

def save_worker():
    global running
    while running or not save_queue.empty():
        try:
            ts, depth, color = save_queue.get()
        except queue.Empty:
            continue

        depth_path = SAVE_DIR / 'depth' / f'depth_{ts}.png'
        color_path = SAVE_DIR / 'color' / f'color_{ts}.jpg'

        cv.imwrite(depth_path, depth)
        cv.imwrite(color_path, color)

        size_kb = (os.path.getsize(depth_path)+os.path.getsize(color_path))/1000

        print(f"Saved! Frame {ts} | {size_kb:.0f} kb")

        save_queue.task_done()

def display():
    global running, current_depth, current_color, current_ts, req_auto

    cv.namedWindow(WIN_NAME)

    cv.createTrackbar('Delay (s)', WIN_NAME, 0, 10, nothing)
    cv.createTrackbar('Depth Overlay %', WIN_NAME, 0, 100, nothing)
    cv.createTrackbar('Max. depth (cm)', WIN_NAME, 3000, 3000, nothing)
    cv.setTrackbarMin('Max. depth (cm)', WIN_NAME, 10)
    cv.createTrackbar('Speckle Size', WIN_NAME, 48, 255, nothing)
    cv.createTrackbar('Speckle Difference', WIN_NAME, 200, 255, nothing)

    while True:
        key = cv.waitKey(1)
        if key == ord('q'):
            running = False
            break
        elif key == ord('s'):
            req_auto = not req_auto
            console.print('Requesting frames: ', '[green]on[/green]' if req_auto else '[red]off[/red]')

        if current_depth is None:
            continue

        if current_ts is not None:
            cv.setWindowTitle(WIN_NAME, f'Frame {current_ts}')
        
        maxSpeckleSize = cv.getTrackbarPos('Speckle Size', WIN_NAME)
        maxSpeckleDiff = cv.getTrackbarPos('Speckle Difference', WIN_NAME)
        maxDepth = cv.getTrackbarPos('Max. depth (cm)', WIN_NAME)*10 #to mm
        depthBlend = cv.getTrackbarPos('Depth Overlay %', WIN_NAME)/100.0

        disp = gcs_utils.visualize(current_depth, current_color, maxSpeckleSize, maxSpeckleDiff, maxDepth, depthBlend)

        cv.imshow(WIN_NAME, disp)

    cv.destroyAllWindows()

def main():
    global running, save_queue

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

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to TCP server...')
    sock.connect((HOST, PORT))
    print('Connected!')

    running = True

    listener_thread = threading.Thread(target=listen, args=(sock,), daemon=True)

    save_thread = threading.Thread(target=save_worker, daemon=True)
    display_thread = threading.Thread(target=display)

    listener_thread.start()
    save_thread.start()
    display_thread.start()

    display_thread.join()
    running = False

    listener_thread.join(timeout=1)
    save_thread.join(timeout=1)
    
    sock.close()

    print('Exiting')

if __name__ == '__main__':
    main()