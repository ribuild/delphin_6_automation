__author__ = 'Christian Kongsgaard'
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import logging
import os
from notifiers.logging import NotificationHandler
import platform

# RiBuild Modules:

try:
    from delphin_6_automation.database_interactions.auth import gmail
except ModuleNotFoundError:
    pass

# -------------------------------------------------------------------------------------------------------------------- #
# LOGGERS


def ribuild_logger(name):

    source_folder = os.path.dirname(os.path.realpath(__file__))
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    if os.path.exists(f'{source_folder}/{name}.log'):
        os.remove(f'{source_folder}/{name}.log')

    fh = logging.FileHandler(f'{source_folder}/{name}.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(fh)

    return logger


def notifiers_logger(name):

    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)

    # create console handler and set level to debug
    message_dict = {'to': 'ocni@dtu.dk',
                    'subject': f'Fatal Error on {platform.node()}',
                    'username': gmail['mail'],
                    'password': gmail['password']}

    nh = NotificationHandler('gmail', defaults=message_dict)
    nh.setLevel(logging.ERROR)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    nh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(nh)

    return logger
