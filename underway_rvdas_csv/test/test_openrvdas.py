from logger.writers.file_writer import FileWriter

def main():
    logger = FileWriter(filename='test.txt')
    logger.write('Wheee')

if __name__ == '__main__':
    main()