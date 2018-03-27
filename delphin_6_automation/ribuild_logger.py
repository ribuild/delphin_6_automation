import logging

# create logger
logger = logging.getLogger('ribuild-debug')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
fh = logging.FileHandler('simulation_worker.log')
fh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(fh)