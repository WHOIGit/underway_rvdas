# Underway RVDAS
An implementation of OpenRVDAS for WHOI's research vessels.

[Full documentation](https://whoi-it.atlassian.net/wiki/spaces/ShipOps/pages/867205128/Underway+Data+Collection+with+OpenRVDAS)

## Usage

###### underway_rvdas.py
  python3 underway_data_monitor.py {--ship (config name)} --shipConfiguration (path to ship config file) --deviceConfiguration (path to device config file)

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

### 2. Start feeder scripts

Run the feeder scripts which will update the database.

These feeder scripts are subpar, and there is a mismatch between the data outputted by the sensors and the data written to DB by the feeder scripts. In the future, this program can be extended to either regenerate feeder scripts on invocation of the program, or consolidate feeder scripts into one absctracted feeder script that makes the feeder scripts for specific devices simpler, less repetitive, and more flexible with format of input data.

```
cd ~/WHOI/underway_rvdas/database/feeders && ./startup.sh
```

### 3. Run underway_data_monitor.py

Next, run the main program which will listen for the data being transmitted, log it, and also output it as UDP data. This data is picked up by the python feeder scripts, which will write it to the database.

The program takes a ship argument, which is the name of a ship configuration. These ship configurations are created and edited by the scripts ```ship_config.py``` and ```device.config.py```. Each ship configuration is a list of defined devices with specified input and output information necessary for updating the database. The concept of ship configurations is primarily to reduce time spent manually editing configuration files, and allowing for the user to quickly swap between two sets of devices between two invocations of the program.

```
cd ~/WHOI/underway_rvdas && python3 device_config.py list
```
```
cd ~/WHOI/underway_rvdas && python3 ship_config.py list
```
```
cd ~/WHOI/underway_rvdas && python3 underway_data_monitor.py --ship test
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
