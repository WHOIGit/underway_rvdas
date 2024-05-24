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
    config_map = {prop['device']: prop for prop in devices}
    for ship in ships:
        ship_config = {'ship': ship['ship'], 'devices': []}
        for device in ship['devices']:
            if device in config_map:
                ship_config['devices'].append(config_map[device])
        input_devices.append(ship_config)
    return input_devices

############################################################################
def setup_listener(device, port):
    readers = [SerialReader(port=port)]
    transforms = [PrefixTransform(prefix=device), TimestampTransform()]
    writers = [LogfileWriter(filebase=f'output/{device}.log')]
    listener = Listener(readers=readers, transforms=transforms, writers=writers)
    print(f'Running listener {device} ({port})')
    listener.run()

############################################################################
# Ship config argument
parser = argparse.ArgumentParser()
parser.add_argument('--shipConfig', help='Path to the device config file', required=True)
parser.add_argument('--deviceConfig', help='Path to the ship config file', required=True)
parser.add_argument('--ship', help='Ship config to run', required=True)
args = parser.parse_args()

# Parse configuration files
ships = parse_ships(args.shipConfig)
devices = parse_devices(args.deviceConfig)
config = [
    {device['device']: prop[prop.find('=')+1:] for prop in device['properties'] if prop.startswith('port=')}
    for conf in filter(lambda x: x['ship'] == args.ship, parse_config(ships, devices))
    for device in conf['devices']
]

# Set up readers, writers, and transforms for each device
print(f'Config complete: {config}')
threads = []
for conf in config:
    for device, port in conf.items():
        thread = threading.Thread(target=setup_listener, args=(device, port))
        thread.start()
        threads.append(thread)
for thread in threads:
    thread.join()
