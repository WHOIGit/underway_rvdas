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
def setup_listener(device, port, data_type):
    print(f'setting up listener for {device} on {port} ({data_type})')
    if data_type == 'serial':
        reader = SerialReader(port=port)
    elif data_type == 'udp':
        reader = UDPReader(port=port)
    readers = [reader]
    transforms = [PrefixTransform(prefix=device), TimestampTransform()]
    writers = [LogfileWriter(filebase=f'output/{device}.log')]
    listener = Listener(readers=readers, transforms=transforms, writers=writers)
    print(f'Running listener {device} ({port})')
    listener.run()

############################################################################

# First, set up logging
LOGGING_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=LOGGING_FORMAT)
LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
logging.getLogger().setLevel(LOG_LEVELS[1])

# Ship config argument
parser = argparse.ArgumentParser()
parser.add_argument('--method', help='The method of data collection to run.', choices=['log', 'serial', 'udp'], nargs='*', required=True)
parser.add_argument('--shipConfig', help='Path to the device config file', required=True)
parser.add_argument('--deviceConfig', help='Path to the ship config file', required=True)
parser.add_argument('--ship', help='Ship config to run', required=True)
parser.add_argument('--interval', help='The amount of time (in seconds) between each data retrieval.', type=int)
args = parser.parse_args()

# Parse configuration files
ships = parse_ships(args.shipConfig)
devices = parse_devices(args.deviceConfig)
# config = [
#     {device['device']: prop[prop.find('=')+1:] for prop in device['properties'] if prop.startswith('port=')}
#     for conf in filter(lambda x: x['ship'] == args.ship, parse_config(ships, devices))
#     for device in conf['devices']
# ]
config = parse_config(ships,devices)

# Logging
if 'log' in args.method:
    # Set up readers, writers, and transforms for each device
    threads = []
    for conf in config:
        for device_conf in conf['devices']:
            device = device_conf['device']
            port = None
            data_type = None
            for prop in device_conf['properties']:
                prop_key, prop_val = prop.split('=')
                print(device_conf, "|", prop_key, "|", prop_val)
                if prop_key == 'port':
                    port = prop_val
                elif prop_key == 'data_type':
                    data_type = prop_val
            thread = threading.Thread(target=setup_listener, args=(device, port, data_type))
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()

############################################################################
# def generate_readers(input_devices):
#     """Generate UDPReader objects from parsed input device data.
#     input_devices   A list of parsed input devices that include (at 
#                     a minimum): the sensor name, IP address(es), 
#                     and socket(s).
#     """
#     readers = []
#     # Listen on IN_SOCKET port
#     for input_device in input_devices:
#         if 'IN_SOCKET' in input_device.properties:
#             # TODO: listen on all DESTINATION_N_SOCKET as well
#             socket = input_device.properties['IN_SOCKET']
#             reader = UDPReader(port=socket)
#             readers.append(reader)
#     return readers

# def generate_transforms(input_devices):
#     """Generate logging transforms from parsed input device data.
#     input_devices   A list of parsed input devices that include (at 
#                     a minimum): the sensor name, IP address(es), 
#                     and socket(s).
#     """
#     transforms = {}
#     # TODO: Remove hardcoded barryserial regex
#     transforms['.*PR[0-9]{1}.*'] = 'barryserial_met' #55300 transmits data as "PR{N},{data 1},{data 2},..."
#     transforms['\\$[A-Z]{5}.*'] = 'barryserial_gps' #55001 transmits data as "${ABCDE},{data 1},{data 2},..."
#     for input_device in input_devices:
#         # TODO: Figure out how to extrapolate device name from recorded sensor data
#         if 'DATA_SOURCE' in input_device.properties:
#             device_name = input_device.properties['DATA_SOURCE'].replace('"', '')
#             regex = f'.*{device_name}.*'
#             transforms[regex] = device_name
#     return PrefixTransform(transforms)

# # Command line input
# parser = argparse.ArgumentParser()
# parser.add_argument('--method', help='The method of data collection to run.', choices=['log', 'serial', 'udp', 'visual'], nargs='*', required=True)
# parser.add_argument('--shipConfig', help='A configuration file for ship configs.', required=True)
# parser.add_argument('--deviceConfig', help='A configuration file for device configs.', required=True)
# # configuration.add_argument('--sensorData', help='A semicolon-delimited set of device mappings to measure. Format: "<device>:<port1>,<port2>,...;"')
# # parser.add_argument('--interval', help='The amount of time (in seconds) between each data retrieval.', type=int)
# # subparsers = parser.add_subparsers(dest='subcommand')
# # log_parser = subparsers.add_parser('log')
# # serial_parser = subparsers.add_parser('serial')
# # udp_parser = subparsers.add_parser('udp')
# # visual = subparsers.add_parser('visual')
# # serial_parser.add_argument('--serialPort', help='This should only show up if method=serial has been specified.')
# args = parser.parse_args()

# # Parse sensor information
# ships = parse_ships(args.shipConfig)
# devices = parse_devices(args.deviceConfig)
# configuration = parse_config(ships, devices)
# # elif args.sensorData:
# # #     input_devices = parse_devices(args.sensorData)
# # else:
# #     input_devices = []
# #     logging.error('No input data is being consumed!')
    
# # Device readers
# readers = generate_readers(configuration)

# # Data transforms
# transforms = []
# if configuration:
#     transforms.append(generate_transforms(configuration))
# transforms.append(TimestampTransform())

# # Text/UDP/serial writers
# writers = []
# if 'log' in args.method:
#     writers.append(LogfileWriter(filebase=f'output/{time.time()}'))
# # elif 'serial' in args.method == 'serial':
# #     ...
# # elif 'udp' in args.method == 'udp':
# #     ..
# # elif args.method == 'visual':
# #     writers.append(...)

# # Start listening
# listener = Listener(
#     readers=readers,
#     transforms=transforms,
#     writers=writers
# )
# listener.run()