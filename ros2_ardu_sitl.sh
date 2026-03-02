source /opt/ros/humble/setup.bash
cd ~/ardu_ws/
colcon build --packages-up-to ardupilot_sitl
source install/setup.bash
ros2 launch ardupilot_sitl sitl_dds_udp.launch.py \
transport:=udp4 \
synthetic_clock:=True \
wipe:=False \
model:=quad \
speedup:=1 \
slave:=0 \
instance:=0 \
defaults:=$(ros2 pkg prefix ardupilot_sitl)/share/ardupilot_sitl/config/default_params/copter.parm,$(ros2 pkg prefix ardupilot_sitl)/share/ardupilot_sitl/config/default_params/dds_udp.parm \
sim_address:=127.0.0.1 \
master:=tcp:127.0.0.1:5760 \
sitl:=127.0.0.1:5501