> [!NOTE]
> This branch, the `simulation` branch, is used for code that will run in a simulated environemnt of the drone.

## Dependencies & Requirements
> [!IMPORTANT]
> For simulation, you **must** use [Ubuntu 22.04](https://releases.ubuntu.com/jammy/).
> There are a few options to get Ubuntu 22.04 running:
> 1) Run inside WSL (Windows Subsystem for Linux)
> 2) Run inside a VM (Virtual Machine).
> 3) Advanced: Dual boot your computer.

> [!TIP]
> For development, you can run [install_simulation.sh](/scripts/install_simulation.sh) for a quick installation of ROS2, ArduPilot SITL, and Gazebo.

- [ROS 2 Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html). ROS 2 Humble is needed for ArduPilot and will require Ubuntu 22.04 to work.
- [ArduPilot SITL for ROS 2](https://ardupilot.org/dev/docs/ros2-sitl.html). ArduPilot's simulator.
- [Gazebo Harmonic](https://gazebosim.org/docs/harmonic/install/) for 3D simulation environment with sensor integration. Gazebo Fortress is compatible with ROS 2 Humble.

Additionally, you should also install the following if you need to:
- [RTAB-Map for ROS2](https://introlab.github.io/rtabmap/). Used for 3D Mapping.
- To install python dependencies, run requirements.txt: `pip install -r requirements.txt`
