import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='log.log'):
    logger = logging.getLogger('meu_logger')
    
    if not logger.hasHandlers():
        handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    logging.getLogger().setLevel(logging.CRITICAL)

    return logger

log = setup_logging()