#!/bin/bash
set -euo pipefail

if ! grep -q "22.04" /etc/os-release; then
    echo "This installer is intended for Ubuntu 22.04."
    exit 1
fi

echo "[!] You are about to install and set up ROS2 Humble, Gazebo, and ArduPilot. PLEASE USE WITH CAUTION!"

while true; do
    read -p "Do you wish to continue? (yes/no): " yn
    case $yn in
        [Yy]* ) echo "Proceeding..."; break;; # Action on Yes and break the loop
        [Nn]* ) echo "Exiting..."; exit;;     # Action on No and exit the script
        * ) echo "Please answer yes or no.";; # Invalid input, loop continues
    esac
done

################
# Locale Setup #
################
echo "Making sure your locale supports UTF-8..."

sudo apt update
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

##############################
# Enable Universe Repository #
##############################

# You will need to add the ROS 2 apt repository to your system.
# First ensure that the Ubuntu Universe repository is enabled.

sudo apt install -y software-properties-common
sudo add-apt-repository universe

########################
# Install ROS 2 Humble #
########################
echo "Installing the ros2-apt-source package..."

# The ros-apt-source packages provide keys and apt source configuration for the various ROS repositories.
# Installing the ros2-apt-source package will configure ROS 2 repositories for your system.
# Updates to repository configuration will occur automatically when new versions of this package are released to the ROS repositories.

sudo apt update
sudo apt install -y curl

ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
sudo apt upgrade -y

# Desktop Install (Recommended): ROS, RViz, demos, tutorials, Development tools.
sudo apt install -y \
    ros-humble-desktop \
    ros-dev-tools \
    python3-colcon-common-extensions \
    python3-vcstool \
    build-essential \
    cmake \
    '~nros-humble-rqt*'

echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

#####################
# Initialize rosdep #
#####################
sudo rosdep init 2>/dev/null || true
rosdep update

#####################
# Install ArduPilot #
#####################
echo "Installing ArduPilot"

sudo apt-get update
sudo apt install -y git gitk git-gui

cd ~
if [ ! -d "ardupilot" ]; then
    echo "Cloning ArduPilot's repository."
    git clone --recurse-submodules https://github.com/ArduPilot/ardupilot
fi

cd ardupilot

echo "Installing required packages"
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile

echo "Building ArduPilot code"
./waf configure --board sitl
./waf copter

##########################
# Create ROS 2 Workspace #
##########################
echo "Creating ROS2 ArduPilot workspace"

mkdir -p ~/ardu_ws/src
cd ~/ardu_ws

echo "This might take a few minutes..."
vcs import --recursive --input  https://raw.githubusercontent.com/ArduPilot/ardupilot/master/Tools/ros2/ros2.repos src

source /opt/ros/humble/setup.bash

rosdep install --from-paths src --ignore-src -r -y

####################################
# Install Micro XRCE-DDS Generator #
####################################
echo "Installing MicroXRCEDDSGen..."

sudo apt install -y default-jre

cd ~/ardu_ws
if [ ! -d "Micro-XRCE-DDS-Gen" ]; then
    git clone --recurse-submodules https://github.com/ardupilot/Micro-XRCE-DDS-Gen.git
fi

cd Micro-XRCE-DDS-Gen
./gradlew assemble

echo "export PATH=\$PATH:$PWD/scripts" >> ~/.bashrc

##################################
# Build ArduPilot ROS2 Workspace #
##################################
echo "Building ArduPilot ROS2 workspace"

cd ~/ardu_ws
colcon build

###########################
# Install Gazebo Harmonic #
###########################
echo "Installing Gazebo Harmonic..."

sudo apt-get install -y curl lsb-release gnupg

sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install -y gz-harmonic

##################################
# Gazebo + ArduPilot Integration #
##################################

#We will clone the required repositories using vcstool and a ros2.repos files:
cd ~/ardu_ws

vcs import --input https://raw.githubusercontent.com/ArduPilot/ardupilot_gz/main/ros2_gz.repos --recursive src

sudo wget https://raw.githubusercontent.com/osrf/osrf-rosdep/master/gz/00-gazebo.list -O /etc/ros/rosdep/sources.list.d/00-gazebo.list

source /opt/ros/humble/setup.bash

rosdep update
rosdep install --from-paths src --ignore-src -y

colcon build

echo "source ~/ardu_ws/install/setup.bash" >> ~/.bashrc

#Done
echo "======================================"
echo "Installation Complete"
echo "======================================"
echo "Open a new terminal or run:"
echo "source ~/.bashrc"