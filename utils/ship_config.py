import argparse
import os
import pprint
import sys

def parse_conf_file(filepath):
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

def create_ship_conf(conf_name, ship_conf, available_devices):
    """Create a new ship configuration.
    conf_name           The name of the new ship configuration.
    ship_conf           The current ship configuration data to be modified.
    available_devices   The list of available devices to modify the 
                        configuration with.
    """
    # Check if configuration already exists
    if next((conf for conf in ship_conf if conf['ship'] == conf_name), None) is not None:
        print(f'Existing configuration for \'{conf_name}\' found. Use \'python3 {os.path.basename(__file__)} edit {conf_name}\' to modify an existing entry.')
        sys.exit()
    device_list = []
    print(f'Available devices:\n{available_devices}\n')
    print(f'Enter \'save\' to save configuration. Enter device name to add to \'{conf_name}\':')
    # Convert all items in available_devices to lowercase for string matching
    available_devices = [i.lower() for i in available_devices]
    # Prompt to continually enter devices until 'save' is inputted
    i = input('  -> ').lower()
    while (i not in ['save', 'exit', 'quit']):
        if i in device_list:
            print(f'    - device {i} already in {conf_name} configuration')
        elif i in available_devices:
            device_list.append(i)
            print(f'    - added {i} to {conf_name}')
        else:
            print(f'    - device {i} not found, try again')
        i = input('  -> ').lower()
    # Add configuration to list
    ship_conf.append({'ship': conf_name, 'devices': device_list})

def update_ship_conf(conf_name, ship_conf, available_devices):
    """Create a new ship configuration.  
    conf_name           The name of the ship configuration to update.
    ship_conf           The current ship configuration data to be modified.
    available_devices   The list of available devices to modify the 
                        configuration with.
    """
    # Retrieve specified configuration
    current_conf = next((conf for conf in ship_conf if conf['ship'] == conf_name), None)
    if current_conf is None:
        print(f'No configuration for \'{conf_name}\' found. Use \'python3 {os.path.basename(__file__)} create {conf_name}\' to create a new entry.')
        sys.exit()
    device_list = current_conf['devices']
    print(f'Available devices:\n{available_devices}\n')
    print(f"Current devices in {conf_name} configuration:\n{current_conf['devices']}\n")
    print(f'Enter \'save\' to save configuration. Enter device name to add to \'{conf_name}\':')
    # Convert all items in available_devices and device_list to lowercase for string matching
    available_devices = [i.lower() for i in available_devices]
    device_list = [i.lower() for i in device_list]
    # Prompt to continually enter devices until 'save' is inputted
    i = input('  -> ').lower()
    while (i not in ['save', 'exit', 'quit']):
        if len(i) < 2 or i[0] not in ['+', '-']:
            print(f'    - input must include a plus (+) or minus (-) followed by a device name to determine whether the device is added or removed from the configuration.')
        else:
            op = i[0]
            device = i[1:]
            # Invalid device
            if device not in available_devices:
                print(f'    - device {device} not found, try again')
            elif op == '+':
                # Adding existing device
                if device in device_list:
                    print(f'    - device {device} already in {conf_name} configuration, cannot add')
                # Successful add device
                else:
                    device_list.append(device)
                    print(f'    - added {device} to {conf_name}')
            elif op == '-':
                # Removing nonexistant device
                if device not in device_list:
                    print(f'    - device {device} not in {conf_name} configuration, cannot remove')
                # Successful remove device
                else:
                    device_list.remove(device)
                    print(f'    - device {device} removed from {conf_name}')
        i = input('  -> ').lower()
    # Add configuration to list
    for conf in ship_conf:
        if conf['ship'] == conf_name:
            conf['devices'] = device_list
    print(f'Configuration editing complete: {ship_conf}')

def rewrite_conf_file(filepath, ship_conf):
    """Confirm intent to save changes and write to file.
    filepath    The path of the file to write to.
    ship_conf   The new ship configuration data to write.
    """
    print(f'\nSaving to file {filepath}:')
    pprint.pp(ship_conf)
    res = input('Proceed (y/n)? ').lower()
    if res == 'y':
        with open(filepath, 'w') as file:
            # Overwrite file with updated ship configurations
            for conf in ship_conf:
                # Ship name in brackets and list one device per line below
                file.write(f"[{conf['ship']}]\n")
                for device in conf['devices']:
                    file.write(f'{device}\n')
                # Line break between ship configurations
                file.write('\n')
        print('Ship configuration(s) saved.')
    else:
        print('Discarding change(s).')
        sys.exit()

# Command line arguments
parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='method')
create_parser = subparser.add_parser('create')
create_parser.add_argument('ship_config', help='The name of the ship configuration to create.')
update_parser = subparser.add_parser('update')
update_parser.add_argument('ship_config', help='The name of the ship configuration to update.')
delete_parser = subparser.add_parser('delete')
delete_parser.add_argument('ship_config', help='The name of the ship configuration to delete.')
list_parser = subparser.add_parser('list')
args = parser.parse_args()

# Ensure a method was specified
if len(sys.argv) < 2:
    print(f'Usage: {os.path.basename(__file__)} {{create <ship_conf> | update <ship_conf> | delete <ship_conf> | list}}')
    sys.exit()

# Retrieve all necessary data for action
method = args.method
conf_file = 'conf/ship.conf'
ship_conf = parse_conf_file(conf_file)

# Check for list method first
if method == 'list':
    print('Ship configurations:')
    [print(f" - {conf['ship']}: {conf['devices']}") for conf in ship_conf]
    sys.exit()

# Check for delete first, to avoid unncessarily loading device list
conf_name = args.ship_config
if method == 'delete':
    # Remove element with conf['ship'] == conf_name
    ship_conf = [conf for conf in ship_conf if conf['ship'] != conf_name]
# Load list of devices from device conf
available_devices = ['barryserial_gps', 'barryserial_met', 'USBL', 'SBE45', 'SBE48', 'POSMV'] #device_conf.get_all() #TODO change this
if method == 'create':
    create_ship_conf(conf_name, ship_conf, available_devices)
if method == 'update':
    update_ship_conf(conf_name, ship_conf, available_devices)

# Rewrite file to match new configuration
rewrite_conf_file(conf_file, ship_conf)