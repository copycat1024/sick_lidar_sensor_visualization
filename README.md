# SICK Pidar Laser Sensor for railway

## Introduction
![Visualization](https://raw.githubusercontent.com/copycat1024/sick_lidar_sensor_visualization/master/pictures/visualization.jpg)

This project use a Lidar laser sensor to detect if someone come too close to a railway.

## Scenarios
![Normal scenarios](https://raw.githubusercontent.com/copycat1024/sick_lidar_sensor_visualization/master/pictures/normal.png)  
Normal scenarios
![Warning scenarios](https://raw.githubusercontent.com/copycat1024/sick_lidar_sensor_visualization/master/pictures/warning.png)  
Warning scenarios
![Danger scenarios](https://raw.githubusercontent.com/copycat1024/sick_lidar_sensor_visualization/master/pictures/danger.png)  
Danger scenarios

## Installation
To run the project:
- Install Python3
- Download the project source code
- Use pip to install dependencies: ``` pip install -r requirement.txt ```, preferably in a virtualenv
- Modify the config.toml file according to your need (select the sensor IP address, danger and warning zones, etc...)
- Run the gui.py file
