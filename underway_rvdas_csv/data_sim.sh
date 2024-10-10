#!/bin/bash

CONFIG_FILE_PATH=/home/befo/Desktop/WHOI/underway/underway_utils/data_sim_config.yaml

# Activate virtual environment
source /opt/openrvdas/venv/bin/activate

# Simulate data
cd /opt/openrvdas/logger/utils/simulate_data.py --config $CONFIG_FILE_PATH &