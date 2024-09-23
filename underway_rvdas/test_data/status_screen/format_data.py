import os
import re
from datetime import datetime

def strip_lines():
    current_directory = os.getcwd()
    for filename in os.listdir(current_directory):
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                lines = file.readlines()
            with open(filename, 'w') as file:
                for line in lines:
                    i = line.find('2')
                    file.write(line[i:] + '\n' if i != -1 else '')

def remove_blank_lines():
    current_directory = os.getcwd()
    for filename in os.listdir(current_directory):
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                lines = file.readlines()
            with open(filename, 'w') as file:
                for line in lines:
                    if line.strip():
                        file.write(line)

def format_timestamps():
    # Traverse through all files in the current directory
    for root, dirs, files in os.walk("."):
        for file in files:
            # Check if the file is a text file (you can modify this condition as per your requirement)
            if file.startswith("ar20240528_2000"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                with open(file_path, 'w') as f:
                    for line in lines:
                        # Extract timestamp from the beginning of each line
                        match = re.match(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+)', line)
                        if match:
                            timestamp = match.group(1)
                            # Convert timestamp to desired format
                            new_timestamp = datetime.strptime(timestamp, "%Y/%m/%d %H:%M:%S.%f").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            line = line.replace(timestamp, new_timestamp, 1)
                        # Write the line back to the file
                        f.write(line)


if __name__ == "__main__":
    # strip_lines()
    # remove_blank_lines()
    format_timestamps()
