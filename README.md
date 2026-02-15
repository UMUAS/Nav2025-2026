# Nav2025-2026 - Overview
This is the repository for the UMUAS Navigation section for the 2025-2026 AEAC SUAS Competition.

The following documentation is intended for anyone intersted in our code. It outlines the objectives of our code, as well as the dependencies and sensors used.

## Dependencies & Requirements
- [ROS 2 Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html). ROS 2 Humble is needed for ArduPilot and will require Ubuntu 22.04 to work.
- [Ubuntu 22.04](https://releases.ubuntu.com/jammy/). Can also be installed inside WSL (Windows Subsystem for Linux) instead of dual booting your computer.
- [RTAB-Map for ROS2](https://introlab.github.io/rtabmap/). Used for 3D Mapping.
- [ArduPilot SITL for ROS 2](https://ardupilot.org/dev/docs/ros2-sitl.html). ArduPilot's simulator.
- [Gazebo Fortress](https://gazebosim.org/docs/fortress/install/) for 3D simulation environment with sensor integration. Gazebo Fortress is compatible with ROS 2 Humble.
- To install python dependencies, run requirements.txt: `pip install -r requirements.txt`

## Other information

Physical components used for Navigation:
- [OAK-D Pro](https://shop.luxonis.com/products/oak-d-pro?variant=42455252402399) - For 3D Mapping, obstacle detection, target detection, and general-purpose camera.
- RTK GPS?
- Payload servos

# Task 1
## 3D Mapping
Send drone camera video stream to ground control station where it will be recorded and used for 3D mapping where a user can measure distances between selected points.

## Progress
- [ ] Easy - DepthAI script that stores IMU + Color + Depth data on the drone's computer (Jetson or Raspberry Pi, TBD). All frames are then collected for 3D mapping.
- [ ] Medium - Create a 3D map from the collected frames. Libraries: [RTAB-Map](https://introlab.github.io/rtabmap/)
- [ ] Easy - Implement a distance measurement tool for the 3D map (might not be needed if the 3D mapping library can already do it)
- [ ] Easy - Payload loading/unloading script

# Task 2
## Stage 1 - Target detection & Initialization
In this stage, the drone should search for any targets. 

Detection of circular targets can be achieved by using a lightweight YOLO model and/or classical computer vision algorithms such as Hough Circle Transform. If detection confidence level is high (for example 75% confident), move to stage 2.

## Stage 2 - Approach target & Target tracking
In this stage, the drone will carefully approach the detected target while continuously tracking it. The drone should be aware of any possible collisions while approaching, stopping if something is too close (for example, 0.5m away). If an approach is obstructed by an obstacle, the drone should attempt moving left or right (but also making sure that it sees where it's going).

Once the drone approached to some distance away (for example, 1m) from the target, it should stabilize (stop moving) and move to stage 3.

If our camera is attached to a gimbal, the gimbal will need to move such that the target is always centered in the camera frame.

### Extras
If at any point the target detection is lost (for more than a few frames), the drone should trace back its path and try a different route. After 3 failed route attempts.

## Stage 3 - Extinguishing
The program should activate the water sprayer and aim at the target. Based on the target's bounding box relative to the camera's frame center, and camera's relative position to the sprayer, a trajectory of the water can be calculated. The trajectory's angle is the same as water sprayer's angle.

The sprayer should be activated for some time (for example, 5 seconds). After that, it should turn off and wait until the target soaked some of the water (for example, 1s after deactivation) and then take a picture of the target being extinguished.

### Extras
If the water stream is strong, the camera should be able to see a line. This line can be helpful when there's strong wind because it provides feedback as to where the water is going (endpoint).

## Progress
- [ ] Medium - Recording a dataset for the YOLO model.
- [ ] Medium - Implementing the target detection script using YOLO and/or classical CV algorithms.
- [ ] Hard - Basic target approach script. This script will attempt to move the drone 1m away from a target using simple left/right/front/back/up/down movements.
  - [ ] Medium - Implement obstacle avoidance to the target approach script.
    - [ ] Hard - Implement path reroute when facing an obstacle.
- [ ] Hard - Water trajectory and activation script.
  - [ ] Easy - Send photo of extinguished target to GCS
- [ ] Combining all scripts into one program
