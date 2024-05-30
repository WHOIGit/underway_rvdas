import argparse
import logging
import pprint
import sys
import threading
import time

sys.path.append('/home/atlas/WHOI/openrvdas')
from logger.listener.listener import Listener
from logger.readers.serial_reader import SerialReader
from logger.readers.udp_reader import UDPReader
from logger.transforms.prefix_transform import PrefixTransform
from logger.transforms.timestamp_transform import TimestampTransform
from logger.writers.logfile_writer import LogfileWriter
from logger.writers.text_file_writer import TextFileWriter
from logger.writers.udp_writer import UDPWriter

############################################################################
def parse_ships(filepath):
    """Parse ship configuration data from a file.
    filepath    The path of the file to parse from.
    """
    ship_conf = []
    current_conf = None
    with open(filepath, 'r') as ship_conf_file:
        for line in ship_conf_file:
            line = line.strip()
            # Ignore comments
            if line.startswith('#'):
                continue
            # New ship conf
            if line.startswith('['):
                if current_conf:
                    ship_conf.append(current_conf)
                current_conf = {'ship': line[1:-1], 'devices': []}
            # Store device as part of current conf if not blank
            elif line != '':
                current_conf['devices'].append(line)
        # Store last entry
        if (current_conf):
            ship_conf.append(current_conf)
    return ship_conf

############################################################################
def parse_devices(filepath):
    """Parse device configuration data from a file.
    filepath    The path of the file to parse from.
    """
    device_conf = []
    current_conf = None
    with open(filepath, 'r') as device_conf_file:
        for line in device_conf_file:
            line = line.strip()
            # Ignore comments
            if line.startswith('#'):
                continue
            # New device conf
            elif line.startswith('['):
                if current_conf:
                    device_conf.append(current_conf)
                current_conf = {'device': line[1:-1], 'properties': []}
            # Store device as part of current conf if not blank
            elif line != '':
                current_conf['properties'].append(line)
        # Store last entry
        if (current_conf):
            device_conf.append(current_conf)
    return device_conf

############################################################################
def parse_config(ships, devices):
    """Combines the parsed ship and device data into one object.
    ships       A list of parsed ship configurations.
    devices     A list of parsed device configurations.
    """
    input_devices = []
    for ship in ships:
        # Create empty config with ship name and no devices
        ship_config = {'ship': ship['ship'], 'devices': []}
        for device in ship['devices']:
            device_config = next((prop for prop in devices if prop['device'] == device), None)
            # Add device to config if part of ship
            if device_config:
                ship_config['devices'].append(device_config)
        input_devices.append(ship_config)
    return input_devices

############################################################################
def setup_listener(device, in_port, input_type, out_destination, out_port):
    # Read serial or UDP data
    readers = []
    if input_type == 'serial':
        readers.append(SerialReader(port=in_port))
    elif input_type == 'udp':
        readers.append(UDPReader(port=in_port))
    # Add timestamp and device name to each record
    transforms = []
    transforms.append(PrefixTransform(prefix=device))
    transforms.append(TimestampTransform())
    # Write text to log file and UDP to appropriate destination
    writers = []
    writers.append(LogfileWriter(filebase=f'output/{device}.log'))
    writers.append(UDPWriter(destination="128.128.214.243", port=int(out_port)))
    # Start listener pipeline
    listener = Listener(readers=readers, transforms=transforms, writers=writers)
    listener.run()

############################################################################

# First, set up logging 
LOGGING_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=LOGGING_FORMAT)
LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
logging.getLogger().setLevel(LOG_LEVELS[log_level])

# Handle command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--shipConfigsFile', help='Path to the device configurations file')
parser.add_argument('--deviceConfigsFile', help='Path to the ship configurations file')
parser.add_argument('--ship', help='Ship config to run', required=True)
# TODO: implement interval?
# parser.add_argument('--interval', help='The amount of time (in seconds) between each data retrieval.', type=int)
args = parser.parse_args()

# Parse configuration files
shipConfigsFile = 'conf/ship.conf' if not args.shipConfigsFile else args.shipConfigsFile
ships = parse_ships(shipConfigsFile)
if not any(config['ship'].lower() == args.ship.lower() for config in ships):
    # Invalid ship configuration
    print(f'Ship configuration {args.ship} not found.')
    sys.exit()
deviceConfigsFile = 'conf/device.conf' if not args.deviceConfigsFile else args.deviceConfigsFile
devices = parse_devices(deviceConfigsFile)
config = parse_config(ships, devices)

# Set up readers, writers, and transforms for each device
threads = []
conf = next((conf for conf in config if conf['ship'] == args.ship), None)
for device in conf['devices']:
    device_name = device['device']
    properties = device['properties']
    in_port = next(prop.split("=")[1] for prop in properties if prop.startswith('in_port='))
    data_type = next(prop.split("=")[1] for prop in properties if prop.startswith('data_type='))
    udp_destination = next(prop.split("=")[1] for prop in properties if prop.startswith('udp_destination='))
    udp_port = next(prop.split("=")[1] for prop in properties if prop.startswith('udp_port='))
    threads.append(threading.Thread(
        target=setup_listener,
        args=(device_name, in_port, data_type, udp_destination, udp_port)
    ))
[thread.start() for thread in threads]
[thread.join() for thread in threads]