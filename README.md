# Playground
Run, share, and play around with your code here.

## Playground #1: Water stream detection using optical flow
Source:

![Result](results/watering_lawn/frame.png)

Optical flow:

![Result](results/watering_lawn/optical_flow.png)

Since water flow will look white/light gray, we can mask threshold the image to remove any other color.

An example of a threshold over saturation channel:

![Result](results/watering_lawn/hsv_saturation.png)

An example of a threshold over value channel:

![Result](results/watering_lawn/hsv_value.png)

Combining the two results gives:

![Result](results/watering_lawn/value_satruation_blend.png)

Optical flow results can be masked with the combined channel results compared to unmasked results, as seen previously:

![Result](results/watering_lawn/masked_optical_flow.png) ![Result](results/watering_lawn/optical_flow.png)

The tiny dots come from the flowers. Can remove it using a speckle filter or a guassian blur.

## Playground #2: Camera example scripts
The following scripts are modified or copied versions of the examples provided by [depthai-python](https://github.com/luxonis/depthai-python):

- [cam_test.py](/oakd_tests/cam_test.py)
- [collision_avoidance.py](/oakd_tests/collision_avoidance.py)
- [imu_gyroscope_accelerometer.py](/oakd_tests/imu_gyroscope_accelerometer.py)