> [!NOTE]
> This branch, the `simulation` branch, is used for code that will run in a simulated environemnt of the drone.

## Dependencies & Requirements
> [!IMPORTANT]
> For simulation, you **must** use [Ubuntu 22.04](https://releases.ubuntu.com/jammy/).
> There are a few options to get Ubuntu 22.04 running:
> - Run inside WSL (Windows Subsystem for Linux)
> - Run inside a VM (Virtual Machine).
> - Advanced: Dual boot your computer.

> [!TIP]
> For development, you can run [install_simulation.sh](/scripts/install_simulation.sh) for a quick installation of ROS2, ArduPilot SITL, and Gazebo.

- [ROS 2 Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html). ROS 2 Humble is needed for ArduPilot and will require Ubuntu 22.04 to work.
- [ArduPilot SITL for ROS 2](https://ardupilot.org/dev/docs/ros2-sitl.html). ArduPilot's simulator.
- [Gazebo Harmonic](https://gazebosim.org/docs/harmonic/install/) for 3D simulation environment with sensor integration. Gazebo Fortress is compatible with ROS 2 Humble.

Additionally, you should also install the following if you need to:
- [RTAB-Map for ROS2](https://introlab.github.io/rtabmap/). Used for 3D Mapping.
- To install python dependencies, run requirements.txt: `pip install -r requirements.txt`

## Installation Guides
The following are the official installation guides for ArduPilot, ROS2, and Gazebo, ordered according to the recommended installation order. These were used to create the [install_simulation.sh](/scripts/install_simulation.sh) script.

1. [ROS2 Humble Installation (Ubuntu)](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)
2. [Configuring ROS2 Environment](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html)
3. [Gazebo Harmonic Installation](https://gazebosim.org/docs/harmonic/install_ubuntu/)
4. [Gazebo Installation for ROS2](https://gazebosim.org/docs/harmonic/ros_installation/)
5. [ArduPilot SITL Installation](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html)
6. [ArduPilot Installation for ROS2](https://ardupilot.org/dev/docs/ros2.html)
7. [ArduPilot with Gazebo integration using ROS2](https://ardupilot.org/dev/docs/ros2-gazebo.html)

## Running Simulation
There are a multiple options to simulate your code in simulation. These will be discussed in this section.
### __Option 1:__ Running the ArduPilot SITL without Gazebo in ROS2
> Check out the guide [ArduPilot SITL using ROS2](https://ardupilot.org/dev/docs/ros2-sitl.html).

To run the ArduPilot SITL in ROS2 without Gazebo, open a terminal and run:
```sh
bash scripts/ros2_ardu_sitl.sh
```

This will open the ArduPilot SITL simulator, but it does not open any windows to visualize the drone. To open the visualization, run

```sh
mavproxy.py --console --map --aircraft test --master=:14550
```

MAVProxy will open an additional console and a map. In the terminal, you will now be able to run MAVLink commands, such as:

```
mode guided
arm throttle
takeoff 40
```

### __Option 2:__ Running the ArduPilot SITL with Gazebo in ROS2
> Check out the guide [Running ArduPilot with Gazebo using ROS2](https://ardupilot.org/dev/docs/ros2-gazebo.html#run-the-simulation).

To run Gazebo and ArduPilot SITL in ROS2, you will need to run on 2 terminals.

**On the first terminal**, run the ArduPilot SITL together with Gazebo. The following example will run the `iris_runway.launch.py` script. This script will open the *iris_runway* Gazebo world, along with ArduPilot SITL, and ROS2 RViz for visualization of the drone's camera.

```sh
ros2 launch ardupilot_gz_bringup iris_runway.launch.py
```

Another useful example provided by ArduPilot is the *iris_maze* world. In this simulation, the drone is equiped with a LiDAR sensor that can be seen in the RViz window.

```sh
ros2 launch ardupilot_gz_bringup iris_maze.launch.py
```

**On the second terminal**, run

```sh
mavproxy.py --console --map --aircraft test --master=:14550
```

MAVProxy will open an additional console and a map. In the terminal, you will now be able to run MAVLink commands.

```
mode guided
arm throttle
takeoff 40
```