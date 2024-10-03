import sys
sys.path.append('/opt/openrvdas')

from logger.readers.cached_data_reader import CachedDataReader
import time

reader = CachedDataReader(data_server='localhost:8766',
                          subscription={'fields':
                              {'GyroHeadingTrue': {'seconds': 0}}})

while True:
    data = reader.read()
    print(f"Read data: {data}")
    time.sleep(1)