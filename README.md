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

Optical flow results can be masked with the combined channel results:
![Result](results/watering_lawn/masked_optical_flow.png)

Compared to previously:

![Result](results/watering_lawn/optical_flow.png)

The tiny dots come from the flowers. Can remove it using a speckle filter or a guassian blur.