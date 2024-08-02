import argparse
import os
import pprint
import sys

def parse_conf_file(filepath):
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

def create_device_conf(conf_name, device_conf, available_properties):
    """Create a new device configuration.
    conf_name               The name of the new device configuration.
    device_conf             The current device configuration data to be modified.
    available_properties    The list of available properties to modify the 
                            configuration with.
    """
    # Check if configuration already exists
    if next((conf for conf in device_conf if conf['device'] == conf_name), None) is not None:
        print(f'Existing configuration for \'{conf_name}\' found. Use \'python3 {os.path.basename(__file__)} edit {conf_name}\' to modify an existing entry.')
        sys.exit()

    properties = {}
    print(f'Creating new configuration for \'{conf_name}\'.\n')

    for prop in available_properties:
        value = input(f'Enter value for {prop}: ').strip()
        properties[prop] = value

    # Add configuration to list
    device_conf.append({'device': conf_name, 'properties': [f"{k}={v}" for k, v in properties.items()]})
    print(f'Configuration for \'{conf_name}\' created successfully.')

def update_device_conf(conf_name, device_conf, available_properties):
    """Update an existing device configuration.  
    conf_name               The name of the device configuration to update.
    device_conf             The current device configuration data to be modified.
    available_properties    The list of available properties to modify the 
                            configuration with.
    """
    # Retrieve specified configuration
    current_conf = next((conf for conf in device_conf if conf['device'] == conf_name), None)
    if current_conf is None:
        print(f'No configuration for \'{conf_name}\' found. Use \'python3 {os.path.basename(__file__)} create {conf_name}\' to create a new entry.')
        sys.exit()

    properties = {prop.split('=')[0]: prop.split('=')[1] for prop in current_conf['properties']}
    print(f'Updating configuration for \'{conf_name}\'.\n')

    for prop in available_properties:
        current_value = properties.get(prop, '')
        value = input(f'Enter value for {prop} [{current_value}]: ').strip()
        if value:
            properties[prop] = value

    # Update configuration in the list
    current_conf['properties'] = [f"{k}={v}" for k, v in properties.items()]
    print(f'Configuration for \'{conf_name}\' updated successfully.')


def rewrite_conf_file(filepath, device_conf):
    """Confirm intent to save changes and write to file.
    filepath    The path of the file to write to.
    device_conf   The new device configuration data to write.
    """
    print(f'\nSaving to file {filepath}:')
    pprint.pp(device_conf)
    res = input('Proceed (y/n)? ').lower()
    if res == 'y':
        with open(filepath, 'w') as file:
            # Overwrite file with updated device configurations
            for conf in device_conf:
                # device name in brackets and list one device per line below
                file.write(f"[{conf['device']}]\n")
                for prop in conf['properties']:
                    file.write(f'{prop}\n')
                # Line break between device configurations
                file.write('\n')
        print('device configuration(s) saved.')
    else:
        print('Discarding change(s).')

# Command line arguments
parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='method')
create_parser = subparser.add_parser('create')
create_parser.add_argument('device_config', help='The name of the device configuration to create.')
update_parser = subparser.add_parser('update')
update_parser.add_argument('device_config', help='The name of the device configuration to update.')
delete_parser = subparser.add_parser('delete')
delete_parser.add_argument('device_config', help='The name of the device configuration to delete.')
list_parser = subparser.add_parser('list')
args = parser.parse_args()

# Ensure a method was specified
if len(sys.argv) < 2:
    print(f'Usage: {os.path.basename(__file__)} {{create <device_conf> | update <device_conf> | delete <device_conf> | list}}')
    sys.exit()

# Retrieve all necessary data for action
method = args.method
conf_file = 'conf/device.conf'
device_conf = parse_conf_file(conf_file)

# Check for list method first
if method == 'list':
    print('device configurations:')
    [print(f" - {conf['device']}: {conf['properties']}") for conf in device_conf]
    sys.exit()

# Check for delete first, to avoid unncessarily loading device list
conf_name = args.device_config
if method == 'delete':
    # Remove element with conf['device'] == conf_name
    device_conf = [conf for conf in device_conf if conf['device'] != conf_name]
# Load list of devices from device conf
available_properties = ['data_type', 'in_port', 'input_type', 'baud_rate', 'udp_destination', 'udp_port']
if method == 'create':
    create_device_conf(conf_name, device_conf, available_properties)
if method == 'update':
    update_device_conf(conf_name, device_conf, available_properties)

# Rewrite file to match new configuration
rewrite_conf_file(conf_file, device_conf)