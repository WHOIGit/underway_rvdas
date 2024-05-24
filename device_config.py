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
    properties = []
    print(f'Available properties:\n{available_properties}\n')
    print(f'Enter \'save\' to save configuration. Enter device name to add to \'{conf_name}\':')
    # Convert all items in available_properties to lowercase for string matching
    available_properties = [i.lower() for i in available_properties]
    # Prompt to continually enter properties until 'save' is inputted
    i = input('  -> ').strip().lower()
    while (i not in ['save', 'done', 'exit', 'quit']):
        z = i.find('=')
        if z == -1:
            print(f'    - property must be in the format: property=value')
        else:
            prop = i[:z]
            # TODO: ensure valid value for each property
            value = i[z + 1:]
            if any(prop in p for p in properties):
                print(f'    - property {prop} already in {conf_name} configuration')
            elif prop in available_properties:
                properties.append(i)
                print(f'    - added {i} to {conf_name}')
            else:
                print(f'    - property {prop} not found, try again')
        i = input('  -> ').lower()
    # Add configuration to list
    device_conf.append({'device': conf_name, 'properties': properties})

def update_device_conf(conf_name, device_conf, available_properties):
    """Create a new device configuration.  
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
    properties = current_conf['properties']
    print(f'Available properties:\n{available_properties}\n')
    print(f'Current properties in {conf_name} configuration:\n{current_conf['properties']}\n')
    print(f'Enter \'save\' to save configuration. Enter property name to add to \'{conf_name}\':')
    # Convert all items in available_properties and device_list to lowercase for string matching
    available_properties = [i.lower() for i in available_properties]
    properties = [i.lower() for i in properties]
    # Prompt to continually enter properties until 'save' is inputted
    i = None
    while (i not in ['save', 'done', 'exit', 'quit']):
        i = input('  -> ').lower()
        z = i.find('=')
        if z == -1:
            print(f'    - property must be in the format: property=value')
            continue
        # Property is in valid format, parse it
        prop, value = i[:z], i[z:]
        # Invalid property
        if prop not in available_properties:
            print(f'    - property {prop} not found, try again')
            continue
        # Check if property needs to be replaced or updated, and add input to properties list
        q = next((p for p in properties if p.startswith(prop)), None)
        properies.append(i)
        # Property already exists, update value
        if q:
            properties.remove(q)
            print(f'    - changed property {prop} for {conf_name}')
        # Property does not exist, add to properties list
        else:
            print(f'    - added property {prop} to {conf_name}')
    # Add configuration to list
    for conf in device_conf:
        if conf['device'] == conf_name:
            conf['properties'] = properties
    print(f'Configuration editing complete: {device_conf}')

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
                file.write(f'[{conf['device']}]\n')
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
    [print(f' - {conf['device']}: {conf['properties']}') for conf in device_conf]
    sys.exit()

# Check for delete first, to avoid unncessarily loading device list
conf_name = args.device_config
if method == 'delete':
    # Remove element with conf['device'] == conf_name
    device_conf = [conf for conf in device_conf if conf['device'] != conf_name]
# Load list of devices from device conf
available_devices = ['type', 'port', 'format'] #device_conf.get_all()
if method == 'create':
    create_device_conf(conf_name, device_conf, available_devices)
if method == 'update':
    update_device_conf(conf_name, device_conf, available_devices)

# Rewrite file to match new configuration
rewrite_conf_file(conf_file, device_conf)