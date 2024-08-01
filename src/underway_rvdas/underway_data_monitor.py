import argparse
import logging
import os
import sys
import threading

from logger.listener.listener import Listener
from logger.readers.serial_reader import SerialReader
from logger.readers.udp_reader import UDPReader
from logger.transforms.prefix_transform import PrefixTransform
from logger.transforms.timestamp_transform import TimestampTransform
from logger.writers.text_file_writer import TextFileWriter
from logger.writers.udp_writer import UDPWriter

UNDERWAY_RVDAS_DIR = os.path.dirname(os.path.abspath(__file__))

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
def setup_listener(device, data_type, in_port, input_type, baud_rate, out_destination, out_port):
    """Sets up the readers, transforms, and writers for a device
    device              The name of the device to listen to
    data_type           The 'type' of incoming data, e.g. SSW, NAV, etc
    in_port             The port for the incoming data
    input_type          The type of incoming data (serial, udp)
    baud_rate           The baud rate of incoming serial data
    out_destination     The IP of the server writing to DB
    out_port            The port to write the outgoing data to
    """
    # Read serial or UDP data
    readers = []
    if input_type == 'serial':
        kwargs = {'port': in_port}
        if baud_rate is not None:
            kwargs['baud_rate'] = baud_rate
        readers.append(SerialReader(**kwargs))
    elif input_type == 'udp':
        readers.append(UDPReader(port=in_port))

    # Add timestamp and device name to each record
    transforms = []
    transforms.append(PrefixTransform(prefix=device))
    TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M:%S.%f"
    transforms.append(TimestampTransform(time_format=TIMESTAMP_FORMAT))

    # Add data type to each record if exists
    data_type and transforms.append(PrefixTransform(prefix=data_type))

    # Write text to log file and UDP to appropriate destination
    writers = []
    writers.append(TextFileWriter(filename=f'output/{device}.log'))
    out_destination and out_port and writers.append(UDPWriter(destination=out_destination, port=int(out_port)))
    
    # Start listener pipeline
    listener = Listener(readers=readers, transforms=transforms, writers=writers)
    listener.run()

############################################################################

def main():
    # First, set up logging 
    LOGGING_FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    logging.getLogger().setLevel(LOG_LEVELS[1])

    # Handle command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--shipConfigsFile', help='Path to the device configurations file')
    parser.add_argument('--deviceConfigsFile', help='Path to the ship configurations file')
    parser.add_argument('--ship', help='Ship config to run', required=True)
    args = parser.parse_args()

    # Parse configuration files
    shipConfigsFile = args.shipConfigsFile if args.shipConfigsFile else os.path.join(UNDERWAY_RVDAS_DIR, 'conf/ship.conf')
    ships = parse_ships(shipConfigsFile)
    if not any(config['ship'].lower() == args.ship.lower() for config in ships):
        # Invalid ship configuration
        print(f'Ship configuration {args.ship} not found.')
        sys.exit()
    deviceConfigsFile = args.deviceConfigsFile if args.deviceConfigsFile else os.path.join(UNDERWAY_RVDAS_DIR, 'conf/device.conf')
    devices = parse_devices(deviceConfigsFile)
    config = parse_config(ships, devices)

    
    # Utility function to read properties
    def _read_property(property):
        return next((prop.split("=")[1] for prop in properties if prop.startswith(property)), None)

    # Set up readers, writers, and transforms for each device
    threads = []
    conf = next((conf for conf in config if conf['ship'] == args.ship), None)
    for device in conf['devices']:
        device_name = device['device']
        properties = device['properties']
        data_type = _read_property('data_type')
        in_port = _read_property('in_port')
        input_type = _read_property('input_type')
        baud_rate = _read_property('baud_rate')
        udp_destination = _read_property('udp_destination')
        udp_port = _read_property('udp_port')
        threads.append(threading.Thread(
            target=setup_listener,
            args=(device_name, data_type, in_port, input_type, baud_rate, udp_destination, udp_port)
        ))
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]

# Start program
if __name__ == '__main__':
    main()