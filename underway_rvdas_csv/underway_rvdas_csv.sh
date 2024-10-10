#!/bin/bash

UNDERWAY_RVDAS_CSV_PATH=/home/befo/Desktop/WHOI/underway/underway_rvdas/underway_rvdas_csv
DATA_SIM_CONFIG_FILE=$UNDERWAY_RVDAS_CSV_PATH/atlantis/data_sim_config.yaml
LOGGER_CONFIG_FILE=$UNDERWAY_RVDAS_CSV_PATH/atlantis/logger_config.yaml

# Activate virtual environment
echo "Activating virtual environment..."
source /opt/openrvdas/venv/bin/activate

# Simulate data
echo "Starting data simulation..."
python3 /opt/openrvdas/logger/utils/simulate_data.py --config $DATA_SIM_CONFIG_FILE &

# Run logger manager
echo "Running logger manager..."
python3 /opt/openrvdas/server/logger_manager.py --config $LOGGER_CONFIG_FILE --start_data_server