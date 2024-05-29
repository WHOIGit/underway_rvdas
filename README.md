# Underway RVDAS
An implementation of OpenRVDAS to allow seamless configuration of devices for research vessels.

## Description

This project is aimed to reduce the headache of configuring old underway data collection systems, such as dsLog. It is designed for simplicity and ease of use, with the goal of reducing as much manual editing of configuration files as possible. Three main features are available:

1. underway_rvdas.py
  This is the main application, and is used to perform the actual data collection. This script reads the configuration information provided and listens for incoming data, forwarding it to the appropriate destination(s).
  This script is still a WIP, it is not complete. It is partially functional, reading hardcoded configuration data from dslog.ini, but does not have the functionality to load a ship configuration yet.

3. device_config.py
  This is a utility script used to set up device configurations. When ran, this script modifies the conf/device.conf file and provides the ability to define, update, and remove sensors and other devices used for underway data collection in any research vessel.

4. ship_conf.py
   This is another utility script, used to set up configurations for ships. When ran, this script modifies the conf/ship.conf file, which maps specific devices to specific configurations used on different vessels, which can be loaded into the underway_rvdas.py script.

The two utility scripts should be used in conjunction to create lists of devices that can be quickly swapped out between invocations of the main application. However, the configuration files may also be manually edited, although this is generally not recommended since the format is not checked and may cause fatal errors in the application if formatted improperly.

####More Info

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

## Demo

### 1. Simulate data

Simulate the data using pre-existing log files from the Armstrong's instruments. OpenRVDAS' logger/utils/simulate_data.py will read the files and transmit the data to specified serial/UDP ports to simulate the data coming in live from sensors on board.

The configuration file specified maps each log file to a specific port. In the case of this configuration, each log file is mapped to a port /tmp/tty_somedevice where the log file's data will be transmitted through serial data. This program also supports transmitting/receiving data through UDP, and is interchangeable with serial.


```
cd ~/WHOI/openrvdas/logger/utils && python3 simulate_data.py --config ~/WHOI/underway_rvdas/test_data/status_screen/sim_status_screen_data.yaml
```

### 2. Run underway_data_monitor.py

Next, run the main program which will listen for the data being transmitted, log it, and also output it as UDP data. This data is picked up by the python feeder scripts, which will write it to the database.

The program takes a ship argument, which is the name of a ship configuration. These ship configurations are created and edited by the scripts ```ship_config.py``` and ```device.config.py```. Each ship configuration is a list of defined devices with specified input and output information necessary for updating the database. The concept of ship configurations is primarily to reduce time spent manually editing configuration files, and allowing for the user to quickly swap between two sets of devices between two invocations of the program.

```
cd ~/WHOI/underway_rvdas
python3 device_config.py list
python3 ship_config.py list
python3 underway_data_monitor.py --ship test
```

### 3. Start feeder scripts

Run the feeder scripts which will update the database.

These feeder scripts are subpar, and there is a mismatch between the data outputted by the sensors and the data written to DB by the feeder scripts. In the future, this program can be extended to either regenerate feeder scripts on invocation of the program, or consolidate feeder scripts into one absctracted feeder script that makes the feeder scripts for specific devices simpler, less repetitive, and more flexible with format of input data.

```
cd ~/WHOI/underway_rvdas/database/feeders && ./startup.sh
```

### 4. View live database updates

Open the SQLite database, run a select statement, wait a moment, and run another select statement. [Compare the result to see the difference in data.](https://www.diffchecker.com/)

```
cd ~/WHOI/underway_rvdas/database/feeders && sqlite3 armstrong.db
```

```
SELECT * FROM array;
```

#

:D