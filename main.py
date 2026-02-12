from pymavlink import mavutil
import autonomy
import asyncio

# This program runs on the drone itself.
# The companion computer (the Jetson) will communicate with the flight controller using MAVLink.

PTCL = 'udp' #Connection protocol:
# IP = 'localhost'
IP = '172.20.80.1'
# IP = '127.20.80.1'
# IP = '192.168.56.1'
PORT = 14550

def main():
    print('Begin program.')
    conn = init_mavlink_connection()


    # Threads:
    # - Heartbeat thread: Continuously send heartbeat (1Hz) to ardupilot.
    # - Camera capture thread: Get depth and rgb streams from the depth camera.
    # - Target detection thread: using the RGB frames, detect target.
    # - Approach target thread: aproach target given depth data and target's location while avoiding obstacles.
    # - Water aim thread: aim at target given depth data and target's location.
    #       When done, request to send to GCS a picture of the extinguished target
    # - Send and receive data from GCS: Any useful data should be sent to GCS. GCS might 

    # Need to properly handle what happens when some thread crashes.
    # Sceneraios:
    # 1) Camera crashes (likely if the camera cpu is at 100%): #TODO
    # 2) Target detection crashes: #TODO
    # 3) No connection with GCS: #TODO

    
    
    print('End of program.')

def init_mavlink_connection():
    global PTCL, IP, PORT
    mavlink_conn = mavutil.mavlink_connection(f"{PTCL}:{IP}:{PORT}")

    # Wait for the first heartbeat
    #   This sets the system and component ID of remote system for the link
    mavlink_conn.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" % (mavlink_conn.target_system, mavlink_conn.target_component))

    # Once connected, use 'the_connection' to get and send messages
    return mavlink_conn

if __name__ == '__main__':
    main()