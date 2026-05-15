import numpy as np
import cv2 as cv

def visualize(depth_frame, color_frame, max_speckle_size, max_speckle_diff, max_depth, depth_blend):
    depth_int16 = depth_frame.astype(np.int16)
    # depth_uint8 = ((depth_frame.copy())/16.0).astype(np.uint8)
    filtered, _ = cv.filterSpeckles(depth_int16, 0, max_speckle_size, max_speckle_diff)
    
    mask_valid = (depth_frame > 0).astype(np.uint8) * 255 #remove invalid depth
    mask_range = (depth_frame < max_depth).astype(np.uint8) * 255 #remove values too high
    mask = cv.bitwise_and(mask_valid, mask_range)

    # colormap = cv.normalize(filtered, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U, mask=mask)
    colormap = np.clip(filtered, 0, max_depth)
    colormap = (colormap/max_depth*255.0).astype(np.uint8)
    # colormap = cv.convertScaleAbs(colormap, alpha=1.0, beta=0.0)
    colormap = cv.applyColorMap(colormap,cv.COLORMAP_TURBO)

    vis_depth = cv.bitwise_and(colormap, colormap, mask=mask)

    if color_frame is None:
        return vis_depth
    else:
        return cv.addWeighted(color_frame, (1.0-depth_blend), vis_depth, depth_blend, 0)