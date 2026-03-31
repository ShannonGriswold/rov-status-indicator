# Status Indicator

## Overview

This package publishes status messages from the ROV on MQTT so that they can be recieved by a status indicator.

## Usage

The luxonis_cam_driver node should be launched automatically with the Operator GUI. To run it separately, you can run

```bash
ros2 launch status_indicator status_indicator_launch.py
```

## Launch files

* **status_indicator_launch.py:** launches the status_indicator node (status_indicator.py)

## Nodes

### status_indicator

Publishes status messages on MQTT and recieves MQTT arm/disarm messages to ROS.

#### Published Topics
TODO: Update the published and subscribed topics
* **`/surface/lux_raw/image_raw`** ([sensor_msgs/msg/Image])

    Raw, unrectified Luxonis streams. Toggles between left & right eyes.

Stereo computations required (computationaly expensive for Luxonis cam's onboard compute):

* **`/surface/rect_left/image_raw`** ([sensor_msgs/msg/Image])

    Rectified left eye Luxonis stream.

* **`/surface/rect_right/image_raw`** ([sensor_msgs/msg/Image])

    Rectified right eye Luxonis stream.

* **`/surface/disparity/image_raw`** ([sensor_msgs/msg/Image])

    Disparity map Luxonis stream.

* **`/surface/depth/image_raw`** ([sensor_msgs/msg/Image])

    Depth map Luxonis stream.