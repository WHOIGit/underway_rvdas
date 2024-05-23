import argparse
import logging
import sys
import time

sys.path.append('/home/atlas/WHOI/openrvdas')
from logger.listener.listener import Listener
from logger.readers.udp_reader import UDPReader
from logger.transforms.prefix_transform import PrefixTransform
from logger.transforms.timestamp_transform import TimestampTransform
from logger.writers.logfile_writer import LogfileWriter
from logger.writers.text_file_writer import TextFileWriter

class InputDevice:
    def __init__(self):
        self.properties = {}

def parse_ini(self, filepath):
    """Parse sensor collection and transmission data from an ini file.
    filepath    The path of the file to parse from. This should be a
                path to a file called dslog.ini.
    """
    inputs = []
    current_input = None
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            # New input device definition
            if line.startswith("[INPUT_"):
                if current_input:
                    inputs.append(current_input)
                current_input = InputDevice()
            # This block should not trigger, the data in the ini 
            # config file is formatted incorrectly if it does
            elif line.startswith("["):
                current_input = None
            # Attribute of current input device
            elif current_input:
                if '=' in line:
                    attr = line.split("=")
                    current_input.properties[attr[0]] = attr[1]
    # Add the last input device to the list
    if current_input:
        inputs.append(current_input)
    return inputs

def generate_readers(self, input_devices):
    """Generate UDPReader objects from parsed input device data.
    input_devices   A list of parsed input devices that include (at 
                    a minimum): the sensor name, IP address(es), 
                    and socket(s).
    """
    readers = []
    # Listen on IN_SOCKET port
    for input_device in input_devices:
        if 'IN_SOCKET' in input_device.properties:
            # TODO: listen on all DESTINATION_N_SOCKET as well
            socket = input_device.properties['IN_SOCKET']
            reader = UDPReader(port=socket)
            readers.append(reader)
    return readers

def generate_transforms(self, input_devices):
    """Generate logging transforms from parsed input device data.
    input_devices   A list of parsed input devices that include (at 
                    a minimum): the sensor name, IP address(es), 
                    and socket(s).
    """
    transforms = {}
    # TODO: Remove hardcoded barryserial regex
    transforms['.*PR[0-9]{1}.*'] = 'barryserial_met' #55300 transmits data as "PR{N},{data 1},{data 2},..."
    transforms['\\$[A-Z]{5}.*'] = 'barryserial_gps' #55001 transmits data as "${ABCDE},{data 1},{data 2},..."
    for input_device in input_devices:
        # TODO: Figure out how to extrapolate device name from recorded sensor data
        if 'DATA_SOURCE' in input_device.properties:
            device_name = input_device.properties['DATA_SOURCE'].replace('"', '')
            regex = f'.*{device_name}.*'
            transforms[regex] = device_name
    return PrefixTransform(transforms)

# Set up logging
LOGGING_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=LOGGING_FORMAT)
LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
logging.getLogger().setLevel(LOG_LEVELS[1])

# Command line input
parser = argparse.ArgumentParser()
parser.add_argument('--method', help='The method of data collection to run.', choices=['log', 'serial', 'udp', 'visual'], nargs='*', required=True)
configuration = parser.add_mutually_exclusive_group(required=True)
configuration.add_argument('--configFile', help='A configuration file that lists the device names, output hosts, and output ports to measure.')
configuration.add_argument('--sensorData', help='A semicolon-delimited set of device mappings to measure. Format: "<device>:<port1>,<port2>,...;"')
parser.add_argument('--interval', help='The amount of time (in seconds) between each data retrieval.', type=int)
# subparsers = parser.add_subparsers(dest='subcommand')
# log_parser = subparsers.add_parser('log')
# serial_parser = subparsers.add_parser('serial')
# udp_parser = subparsers.add_parser('udp')
# visual = subparsers.add_parser('visual')
# serial_parser.add_argument('--serialPort', help='This should only show up if method=serial has been specified.')
args = parser.parse_args()

# Parse sensor information
if args.configFile:
    input_devices = parse_ini(args.configFile)
# elif args.sensorData:
#     input_devices = parse_devices(args.sensorData)
else:
    input_devices = []
    logging.error('No input data is being consumed!')
    
# Device readers
readers = generate_readers(input_devices)

# Data transforms
transforms = []
if input_devices:
    transforms.append(generate_transforms(input_devices))
transforms.append(TimestampTransform())

# Text/UDP/serial writers
writers = []
if 'log' in args.method:
    writers.append(LogfileWriter(filebase=f'output/{time.time()}'))
# elif 'serial' in args.method == 'serial':
#     ...
# elif 'udp' in args.method == 'udp':
#     ..
# elif args.method == 'visual':
#     writers.append(...)

# Start listening
listener = Listener(
    readers=readers,
    transforms=transforms,
    writers=writers
)
listener.run()