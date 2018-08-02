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
    gmail = {'mail': None, 'password': None}

# -------------------------------------------------------------------------------------------------------------------- #
# LOGGERS


def ribuild_logger(name):

    source_folder = os.environ.get("_MEIPASS2", os.path.abspath("."))

    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # create console handler and set level to debug
    if os.path.exists(f'{source_folder}/{name}.log'):
        try:
            os.remove(f'{source_folder}/{name}.log')
        except PermissionError:
            pass

    # File Handler
    fh = logging.FileHandler(f'{source_folder}/{name}.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Notification Handler
    message_dict = {'to': 'ocni@dtu.dk',
                    'subject': f'Fatal Error on {platform.node()}',
                    'username': gmail['mail'],
                    'password': gmail['password']}
    nh = NotificationHandler('gmail', defaults=message_dict)
    nh.setLevel(logging.ERROR)
    nh.setFormatter(formatter)
    logger.addHandler(nh)

    # Stream Handler
    sh = logging.StreamHandler()
    stream_formatter = logging.Formatter('%(message)s')
    sh.setFormatter(stream_formatter)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)

    return logger
