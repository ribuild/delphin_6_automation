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

# -------------------------------------------------------------------------------------------------------------------- #
# LOGGERS

loggers = {}


def ribuild_logger(name: str='delphin_6_automation'):
    global loggers

    source_folder = os.environ.get("_MEIPASS2", os.path.abspath("."))

    if loggers.get(name):
        return loggers.get(name)

    else:
        # create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')

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
        message_dict = {'message': f'Fatal Error on {platform.node()}',
                        'webhook_url': 'https://hooks.slack.com/services/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'}
        nh = NotificationHandler('slack', defaults=message_dict)
        nh.setLevel(logging.WARNING)
        nh.setFormatter(formatter)
        logger.addHandler(nh)

        # Stream Handler
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)
        loggers[name] = logger

        return logger
