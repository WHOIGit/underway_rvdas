# Underway RVDAS
An implementation of OpenRVDAS to allow seamless configuration of devices for research vessels.

## Description

This project is aimed to reduce the headache of configuring old underway data collection systems, such as dsLog. It is designed for simplicity and ease of use, with the goal of reducing as much manual editing of configuration files as possible. Three main features are available:

1. underway_rvdas.py
  This is the main application, and is used to perform the actual data collection. This script reads the configuration information provided and listens for incoming data, forwarding it to the appropriate destination(s).

2. device_config.py
  This is a utility script used to set up device configurations. When ran, this script modifies the conf/device.conf file and provides the ability to define, update, and remove sensors and other devices used for underway data collection in any research vessel.

3. ship_conf.py
   This is another utility script, used to set up configurations for ships. When ran, this script modifies the conf/ship.conf file, which maps specific devices to specific configurations used on different vessels, which can be loaded into the underway_rvdas.py script.

The two utility scripts should be used in conjunction to create lists of devices that can be quickly swapped out between invocations of the main application. However, the configuration files may also be manually edited, although this is generally not recommended since the format is not checked and may cause fatal errors in the application if formatted improperly.

## Usage

###### underway_rvdas.py
  python3 underway_rvdas.py --method {log|serial|udp} --shipConfiguration (ship configuration name)

###### device_config.py
  python3 device_config.py {create (device name)|update (device name)|delete (device name)|list}

###### ship_config.py
  python3 ship_config.py {create (config name)|update (config name)|delete (config name)|list}

#

:D
