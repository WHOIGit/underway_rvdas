import argparse
import configparser
import logging
import pprint
import random
import re
from collections import defaultdict
from datetime import datetime

def get_abstract_array_element(n):
    # TODO: get abstract array element n
    return random.uniform(5, 95)

def get_derived_data_element(n):
    # TODO: get derived data element n
    return f"{random.uniform(0, 10)}_but_derived"

def setup_listeners(root_dir, inputs, outputs):
    print(root_dir)
    pprint.pp(inputs)
    pprint.pp(outputs)
    

    # # Add datetime then prefix to beginning of record
    # dt = datetime.today()
    # record = dt.strftime('%Y/%m/%d') + output_delimeter + dt.strftime('%H:%M:%S.%f')[:-3] + output_delimeter
    # output_prefix = config[section].get('output_prefix', None)
    # if output_prefix:
    #     record += output_prefix + output_delimeter

    # # Add data elements to record
    # for outfield_data_element in outfield_data_elements:
    #         # Key is outfield_abstract_index_n
    #         if outfield_data_element.startswith(outfield_data_element_types[0]):
    #             n = outfield_data_element[len(outfield_data_element_types[0]):]
    #             array_element = get_abstract_array_element(n)
    #             record += str(array_element) + output_delimeter
    #         # Key is outfield_type_n
    #         elif outfield_data_element.startswith(outfield_data_element_types[1]):
    #             n = outfield_data_element[len(outfield_data_element_types[1]):]
    #             derived_data_element = get_derived_data_element(n)
    #             record += derived_data_element + output_delimeter

def startswith_filter(filter):
    if isinstance(filter, (list, tuple)):
        return lambda element: any(element.startswith(filter_item) for filter_item in filter)
    return lambda element: element.startswith(filter)

# def extract_data(config, section, filter, datatype):
#     data_filter = startswith_filter(filter)
#     data_keys = filter(data_filter, config.options(section))
#     data_values = [{ key: config[section].get(key, '').replace('"', '') } for key in parse_datatype_keys]
#     for key in data_keys:
#         if datatype == int:
#             value = config[section].getint(key, -1)
#         elif datatype == bool:
#             value = config[section].getboolean(key, false)
#         else:
#             value = config[section].get(key, '').replace('"', '')
#         data_values.append({
#             key: 
#         })

def validate_config(config):
    ALLOWED_KEYS = [
        # General
        'root_dir', 'daily_logfiles_flag', 
        # Inputs
        'input_type', 'in_port', 'in_file', 'input_enable', 'parse_datatype_n', 'parse_abstract_index_n', 'must_contain_n', 'must_not_contain_n', 
        # Derived
        'temperature_abstract_index', 'salinity_abstract_index', 'output_precision', 
        'raw_pressure_abstract_index', 'sensor_height',
        'wind_dir_abstract_index', 'wind_speed_abstract_index', 'cog_abstract_index', 'sog_abstract_index', 'hdg_abstract_index',
        # Outputs
        'output_enable', 'output_interval', 'date_header_string', 'time_header_string', 'output_prefix', 'output_delimeter', 'output_file_format', 'bad_data_string', 'use_file_header', 'destination_prefix', 'destination_n_enable', 'destination_n_type', 'destination_n_ip', 'destination_n_port', 'destination_n_pathname', 'destination_n_filename_prefix', 'destination_n_filename_extension', 'outfield_abstract_index_n', 'outfield_type_n', 'outfield_header_string_n',
        'ship_call_sign', 'ship_name', 'noaa_version'
    ]
    # Ensure no invalid keys exist in the config
    for section in config.sections():
        for option in config.options(section):
            option = re.sub(r'_(\d+)', r'_n', option)
            if option not in ALLOWED_KEYS:
                raise ValueError(f'Invalid key in config: {option}')

def main():
    # First, set up logging 
    LOGGING_FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    logging.getLogger().setLevel(LOG_LEVELS[1])

    # Handle command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--configFile', help='Path to the configuration file', default='conf/underway_rvdas_csv.conf')
    args = parser.parse_args()
    
    # Parse config
    config = configparser.ConfigParser(strict=False)
    config.read(args.configFile)
    validate_config(config)

    # General section
    root_dir = config['general']['root_dir']
    daily_logfiles_flag = config['general'].getboolean('daily_logfiles_flag', True)

    # Inputs section
    inputs = {}
    input_filter = startswith_filter('input_')
    for section in filter(input_filter, config.sections()):
        # Check if input is enabled
        enabled = config[section].getboolean('input_enable', True)
        if not enabled:
            continue

        # Input type is required
        input_type = config[section]['input_type'].replace('"', '')
        inputs[section] = { 'input_type': input_type }
        if input_type == 'udp':
            # In port is required if input is udp
            in_port = config[section].getint('in_port', None)
            if not in_port:
                raise ValueError(f'An input port must be specified for udp inputs. Offending input: {section}')
            inputs[section]['in_port'] = in_port
        elif input_type == 'file':
            # In file is required if input is file
            in_file = config[section].get('in_file', None)
            if not in_file:
                raise ValueError(f'An input file must be specified for file inputs. Offending input: {section}')
            inputs[section]['in_file'] = in_file
        else:
            raise ValueError(f"The value for input_type must be either 'udp' or 'file', got: {input_type}")

        # Parse datatype values
        parse_datatype_filter = startswith_filter('parse_datatype_')
        parse_datatype_keys = filter(parse_datatype_filter, config.options(section))
        parse_datatypes = [{ key: config[section].get(key, '').replace('"', '') } for key in parse_datatype_keys]

        # Parse abstract indexes
        parse_abstract_index_filter = startswith_filter('parse_abstract_index_')
        parse_abstract_index_keys = filter(parse_abstract_index_filter, config.options(section))
        parse_abstract_indexes = [{ key: config[section].getint(key, -1)} for key in parse_abstract_index_keys]

        # Must contain values
        must_contain_filter = startswith_filter('must_contain_')
        must_contain_keys = filter(must_contain_filter, config.options(section))
        must_contain = [{ key: config[section].get(key).replace('"', '').split(',') } for key in must_contain_keys ]

        # Must not contain values
        must_not_contain_filter = startswith_filter('must_not_contain_')
        must_not_contain_keys = filter(must_not_contain_filter, config.options(section))
        must_not_contain = [{ key: config[section].get(key).replace('"', '').split(',') } for key in must_not_contain_keys ]

        # Store data in inputs array
        inputs[section]['parse_datatypes'] = parse_datatypes
        inputs[section]['parse_abstract_indexes'] = parse_abstract_indexes
        inputs[section]['must_contain'] = must_contain
        inputs[section]['must_not_contain'] = must_not_contain
        
    # Derived values section
    derived_filter = startswith_filter(['barometer_', 'ssv_', 'truewind_'])
    for section in filter(derived_filter, config.sections()):
        pass

    # Outputs section
    outputs = {}
    output_filter = startswith_filter('output_')
    for section in filter(output_filter, config.sections()):
        # Check if output is enabled
        enabled = config[section].getboolean('output_enable', True)
        if not enabled:
            continue

        output_prefix = config[section].get('output_prefix', '').replace('"', '')
        output_delimeter = config[section].get('output_delimeter', ', ').replace('"', '')
        outputs[section] = {
            'output_prefix': output_prefix,
            'output_delimeter': output_delimeter
        }

        # Build header string unless specified otherwise
        use_file_headers = config[section].getboolean('use_file_headers', True)
        if use_file_headers:
            outputs[section]['date_header_string'] = config[section].get('date_header_string', 'DATE_GMT').replace('"', '')
            outputs[section]['time_header_string'] = config[section].get('time_header_string', 'TIME_GMT').replace('"', '')
            outfield_header_string_filter = startswith_filter('outfield_header_string_')
            outfield_header_string_keys = filter(outfield_header_string_filter, config.options(section))
            outfield_header_strings = [{ key: config[section].get(key).replace('"', '') } for key in outfield_header_string_keys ]
            outputs[section]['outfield_header_strings'] = outfield_header_strings

        # Outfield data elements
        outfield_abstract_index_filter = startswith_filter('outfield_abstract_index_')
        outfield_abstract_index_keys = filter(outfield_abstract_index_filter, config.options(section))
        outfield_abstract_indexes = [{ key: config[section].getint(key, -1) } for key in outfield_abstract_index_keys ]
        outfield_type_filter = startswith_filter('outfield_type_')
        outfield_type_keys = filter(outfield_type_filter, config.options(section))
        outfield_types = [{ key: config[section].get(key).replace('"', '') } for key in outfield_type_keys ]
        outfield_data_elements = outfield_abstract_indexes + outfield_types


        # Destinations
        destinations = []
        destination_prefix = config[section].get('destination_prefix', '').replace('"', '')
        destinations.append({ 'destination_prefix': destination_prefix })
        destination_filter = startswith_filter('destination_')
        all_destinations = filter(destination_filter, config.options(section))
        groups = defaultdict(list)
        # Sort destinations into sublists
        for key in all_destinations:
            match = re.match(r'destination_(\d+)_(\w+)', key)
            if match:
                number, command = match.groups()
                # Do not add enabled flag to list
                if command != 'enable':
                    groups[int(number)].append({ key: config[section].get(key).replace('"', '') })
        for number, items in sorted(groups.items()):
            # Only add desination if enabled
            if config[section].getboolean(f'destination_{number}_enable', True):
                destinations.append({f'destination_{number}': items})

        # TODO: if destination_type is udp, ensure ip and port are set

        # Store data in outputs array
        outputs[section]['outfield_data_elements'] = outfield_data_elements
        outputs[section]['destinations'] = destinations

    # Create the OpenRVDAS components
    setup_listeners(root_dir, inputs, outputs)
        

if __name__ == '__main__':
    main()


# Add data elements to record
# for outfield_data_element in outfield_data_elements:
#     # Key is outfield_abstract_index_n
#     if outfield_data_element.startswith(outfield_data_element_types[0]):
#         n = outfield_data_element[len(outfield_data_element_types[0]):]
#         array_element = get_abstract_array_element(n)
#         record += str(array_element) + output_delimeter
#     # Key is outfield_type_n
#     elif outfield_data_element.startswith(outfield_data_element_types[1]):
#         n = outfield_data_element[len(outfield_data_element_types[1]):]
#         derived_data_element = get_derived_data_element(n)
#         record += derived_data_element + output_delimeter

# # Strip last output delimeter
# record = record[:-len(output_delimeter)]
# print(record)

# Send parsed data to destinations
    
# Set up readers, writers, and transforms for each device
# threads = []
# for device in conf['devices']:
#     device_name = device['device']
#     properties = device['properties']
#     data_type = _read_property('data_type')
#     in_port = _read_property('in_port')
#     input_type = _read_property('input_type')
#     baud_rate = _read_property('baud_rate')
#     udp_destination = _read_property('udp_destination')
#     udp_port = _read_property('udp_port')
#     threads.append(threading.Thread(
#         target=setup_listener,
#         args=(device_name, data_type, in_port, input_type, baud_rate, udp_destination, udp_port)
#     ))
# [thread.start() for thread in threads]
# [thread.join() for thread in threads]
            

            # # Date and time columns
            # date_header_string = config[section].get('date_header_string', 'DATE_GMT')
            # time_header_string = config[section].get('time_header_string', 'TIME_GMT')
            # header_string = date_header_string + output_delimeter + time_header_string + output_delimeter + output_prefix + output_delimeter
            # # Outfield header strings
            # outfield_header_string_filter = startswith_filter('outfield_header_string_')
            # outfield_header_strings = list(filter(outfield_header_string_filter, config.options(section)))
            # for outfield_header_string in outfield_header_strings:
            #     header_string += config[section][outfield_header_string] + output_delimeter