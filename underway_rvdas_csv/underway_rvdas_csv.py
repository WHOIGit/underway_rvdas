import argparse
import configparser
import logging
import pprint
import random
from datetime import datetime

def get_abstract_array_element(n):
    # TODO: get abstract array element n
    return random.uniform(5, 95)

def get_derived_data_element(n):
    # TODO: get derived data element n
    return f"{random.uniform(0, 10)}_but_derived"

def setup_listeners(root_dir, inputs, outputs):
    # print(root_dir)
    # pprint.pp(inputs)
    # pprint.pp(outputs)

    for output in outputs:
        pass

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

        # Input type is required for each input
        input_type = config[section]['input_type'].replace('"', '')
        if input_type == 'udp':
            # In port is required if input is udp
            pass
        elif input_type == 'file':
            # In file is required if input is file
            pass
        else:
            raise ValueError(f"The value for input_type must be either 'udp' or 'file', got: {input_type}")
        
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

        # Build header string unless specified otherwise
        output_prefix = config[section].get('output_prefix', '')
        output_delimeter = config[section].get('output_delimeter', ', ').replace('"', '')
        use_file_headers = config[section].getboolean('use_file_headers', True)
        if use_file_headers:
            # Date and time columns
            date_header_string = config[section].get('date_header_string', 'DATE_GMT')
            time_header_string = config[section].get('time_header_string', 'TIME_GMT')
            header_string = date_header_string + output_delimeter + time_header_string + output_delimeter
            # Outfield header strings
            outfield_header_string_filter = startswith_filter('outfield_header_string_')
            outfield_header_strings = list(filter(outfield_header_string_filter, config.options(section)))
            for outfield_header_string in outfield_header_strings:
                header_string += config[section][outfield_header_string] + output_delimeter
        # Strip last output delimeter
        header_string = header_string[:-len(output_delimeter)].replace('"', '')

        # Outfield data elements
        outfield_data_element_types = ['outfield_abstract_index_', 'outfield_type_']
        outfield_data_element_filter = startswith_filter(outfield_data_element_types)
        outfield_data_elements = list(filter(outfield_data_element_filter, config.options(section)))

        # Destinations
        destination_filter = startswith_filter('destination_')
        destinations = list(filter(destination_filter, config.options(section)))
        print(destinations)

        # Store data in outputs array
        outputs[section] = {
            'output_prefix': output_prefix,
            'output_delimeter': output_delimeter,
            'outfield_data_elements': outfield_data_elements
        }
        if use_file_headers:
            outputs[section]['header_string'] = header_string

    setup_listeners(root_dir, inputs, outputs)
        
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

if __name__ == '__main__':
    main()