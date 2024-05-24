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

### How It's Used

First, ship_config.py and device_config.py are used to edit the ship/ship.conf and conf/device.conf files. These are configuration files that will replace dslog.ini. The configurations for devices list out device names and ports, although some more attributes potentially may need to be added later. The configurations for ships just have a list of device names that are used by that particular ship configuration. For example, a ship config "armstrong_gps" may list the GPS devices needed by Armstrong, "armstrong_research" may list out sensors used to measure temperature, density, etc, and "armstrong_main" may list out all instruments used by Armstrong for any purpose. The scripts do this via command line I/O.

Next, the configuration files as well as the specific ship configuration to run are passed into test_stream.py. The configurations are then parsed, and for each device specified in the active configuration, a "Listener" is set up. This Listener contains several subcomponents. It has either a SerialReader or a UDPReader. The SerialReader listens for serial data - a good test of the program is using data outputted by the simulate_data script, which is provided by OpenRVDAS and being invoked with the test data provided by OpenRVDAS. The UDPReader does the same, except for reading UDP data. A good test of this functionality is using data transmitted by Barryserial in Smith. The Listener also has a PrefixTransform, which appends the device name to the data being streamed. It also has a TimestampTransform, which like the name suggests, appends a timestamp. Finally, the Listener contains a LogfileWriter, which logs the transformed incoming data to a log file. Logs are configured to send to a separate file for each instrument, but this can be changed to send several sensors to a single log file, or to send all sensors to a single log file, depending on how the data will be consumed.

Finally, all Listeners are invoked with the run() method. Each Listener waits for incoming information, and pushes it down the pipeline when data is transmitted: (sensor - simulated by simulate_data) --> SerialReader --> PrefixTransform --> TimestampTransform --> LogfileWriter. Voila, data is transmitted, transformed, and logged to the right place.

## Usage

###### underway_rvdas.py
  python3 underway_data_monitor.py --method {log|serial|udp} --shipConfiguration (path to ship config file) --deviceConfiguration (path to device config file) --ship (ship configuration to use)

###### device_config.py
  python3 device_config.py {create (device name)|update (device name)|delete (device name)|list}

###### ship_config.py
  python3 ship_config.py {create (config name)|update (config name)|delete (config name)|list}

#

:D
