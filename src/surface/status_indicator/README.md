# Status Indicator

## Overview

This package publishes status messages from the ROV on MQTT so that they can be recieved by a status indicator.

## Usage

The bridge and status_indicator nodes should be launched automatically with the Operator GUI. To run it separately, you can run

```bash
ros2 launch status_indicator status_indicator_launch.py
```

## Launch files

* **status_indicator_launch.py:** launches the status_indicator node (status_indicator.py) and bridge node (bridge.py)

## Nodes

### status_indicator

Saves the state of simulated status messages that are to be sent to the status indicator.

#### Published Topics
* **`/surface/indicator/vehicleState`** ([rov_msgs/msg/VehicleState])

    The vehicle state that is being simulated on the status indicator.

* **`/surface/indicator/flooding`** ([rov_msgs/msg/Flooding])

    The flooding state that is being simulated on the status indicator.

#### Subscribed Topics
* **`/surface/indicator/changeVehicleState`** ([rov_msgs/msg/VehicleState])

    Request to change the vehicle state that is being simulated on the status indicator.

* **`/surface/indicator/changeFlooding`** ([rov_msgs/msg/Flooding])

    Request to change flooding state that is being simulated on the status indicator.

* **`/surface/indicator/arm`** ([std_msgs/msg/Bool])

    Request to change the armed state of the simulated status indicator.

#### Parameters

* **`status-simulation`** (bool, default: False)

    Whether or not to simulate the robot state to the status indicators.

### bridge

Recieves ROS messages about the status of the robot and publishes them on MQTT to the connected status indicators.

#### Published Topics
* **`/surface/indicator/arm`** ([std_msgs/msg/Bool])

    Request to change the simulated armed state from one of the status indicators.

#### Subscribed Topics
* **`/surface/indicator/vehicleState`** ([rov_msgs/msg/VehicleState])

    The simulated vehicle state sent to the status indicator.

* **`/surface/indicator/flooding`** ([rov_msgs/msg/Flooding])

    The simulated flooding state sent to the status indicator.

* **`/surface/vehicle_state_event`** ([rov_msgs/msg/VehicleState])

    The real vehicle state sent to the status indicator.

* **`/surface/flooding`** ([rov_msgs/msg/Flooding])

    The real flooding state sent to the status indicator.

#### Services
* **`/surface/addStatusIndicator`** ([rov_msgs/srv/IpStatus])

    Connect a status indicator to the bridge.

* **`/surface/arming`** ([rov_msgs/srv/VehicleArming])

    Request to change the real armed state of the robot.

#### Parameters

* **`status-simulation`** (bool, default: False)

    Whether or not to simulate the robot state to the status indicators.


[rov_msgs/msg/VehicleState]: ../../rov_msgs/msg/VehicleState.msg
[rov_msgs/msg/Flooding]: ../../rov_msgs/msg/Flooding.msg
[rov_msgs/srv/IpStatus]: ../../rov_msgs/srv/IpStatus.srv
[rov_msgs/srv/VehicleArming]: ../../rov_msgs/srv/VehicleArming.srv