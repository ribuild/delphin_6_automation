import logging
import os


def ribuild_logger(name):

    source_folder = os.path.dirname(os.path.realpath(__file__))
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    fh = logging.FileHandler(f'{source_folder}/{name}.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(fh)

    return logger
