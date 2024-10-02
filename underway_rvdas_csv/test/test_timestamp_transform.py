from logger.listener.listener import Listener
from logger.readers.TextFileReader import TextFileReader
from logger.transforms.timestamp_transform import TimestampTransform
from logger.writers.text_file_writer import TextFileWriter
import logging

if __name__ == '__main__':
    LOGGING_FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    logging.getLogger().setLevel(LOG_LEVELS[1])

    reader = TextFileReader(file_spec='NBP1406_tsg2-2014-08-01', interval=1)

    tf = f'%Y/%m/%d, %H:%M:%S.%f, record'
    transform = TimestampTransform(time_format=tf)

    writer = TextFileWriter(filename='output.txt')

    listener = Listener(readers=[reader], transforms=[transform], writers=[writer])
    listener.run()