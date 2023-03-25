import logging
import os
import random
import uuid
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


BANNER_MSG = ('\n'
    + '     ____  _                         ___                 \n'
    + '    / __ \\(_)___ ___  ____ ______   /   |  ____  ____   \n'
    + '   / / / / / __ `__ \\/ __ `/ ___/  / /| | / __ \\/ __ \\\n'
    + '  / /_/ / / / / / / / /_/ (__  )  / ___ |/ /_/ / /_/ /   \n'
    + ' /_____/_/_/ /_/ /_/\\__,_/____/  /_/  |_/ .___/ .___/   \n'
    + '                                       /_/   /_/         \n'
    + '\n'
    + ' =====================================================\n')
DEFAULT_SEED = 42
LOG_LEVELS = [
    logging.NOTSET,
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]
LOGS_PATH = os.path.join('artifacts', 'logs')


def set_seed(seed: int = DEFAULT_SEED) -> None:
    """Fix seed to be used in the random processes."""
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    # If using numpy or Tensorflow, add the following lines too:
    # > np.random.seed(seed)
    # > tf.random.set_seed(seed)


def build_logger(
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
