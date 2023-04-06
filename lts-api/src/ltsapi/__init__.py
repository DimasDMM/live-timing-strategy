import logging
import os
import uuid


# Use as prefix for every call
API_VERSION = 'v1'

# Logger config
LOG_LEVELS = [
    logging.NOTSET,
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]
LOGS_PATH = os.path.join('artifacts', 'logs')


def _build_logger(
        name: str,
        verbosity: int = 2) -> logging.Logger:
    """Build a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS[verbosity])
    if verbosity == 0:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s] %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    rnd_id = uuid.uuid4().hex
    os.makedirs(LOGS_PATH, exist_ok=True)
    file_name = os.path.join(LOGS_PATH, f'{name}_{rnd_id}.log')
    file_handler = logging.FileHandler(file_name)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
