# Nav2025-2026
Repository for Navigation Section.

Sensors used for Navigation:
- [OAK-D Pro PoE](https://shop.luxonis.com/products/oak-d-pro-poe?variant=42469208916191)

The following outlines the objectives of our code.

# Task 1
## 3D Mapping
Send drone camera video stream to ground control station where it will be recorded and used for 3D mapping where a user can measure distances between selected points.

## Progress
- [ ] Easy - DepthAI script that sends a IMU + Color + Depth streams to the ground control station. All frames are then collected for 3D mapping.
- [ ] Medium - Create a 3D map from the collected frames. Libraries: [nvblox](https://nvidia-isaac.github.io/nvblox/), Spectacular AI
- [ ] Easy - Implement a distance measurement tool for the 3D map (might not be needed if the 3D mapping library can already do it)
- [ ] Easy - Payload loading/unloading script

# Task 2
## Stage 1 - Target detection & Initialization
In this stage, the drone should search for any targets. 

Detection of circular targets can be achieved by using a lightweight YOLO model and/or classical computer vision algorithms such as Hough Circle Transform. If detection confidence level is high (for example 75% confident), move to stage 2.

## Stage 2 - Approach target & Target tracking
In this stage, the drone will carefully approach the detected target while continuously tracking it. The drone should be aware of any possible collisions while approaching, stopping if something is too close (for example, 0.5m away). If an approach is obstructed by an obstacle, the drone should attempt moving left or right (but also making sure that it sees where it's going).

Once the drone approached to some distance away (for example, 1m) from the target, it should stabilize (stop moving) and move to stage 3.

If camera is attached to a gimbal, the gimbal will need to move such that the target is always centered in the camera frame.

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
