import os
import logging
from datetime import datetime

LOG_ROOT_PATH = "logs"


def init_logger_simple():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


def init_logger(config_path: str):
    """
    Initialize logger, the logging file will be saved in
    `logs/{data_name}/{conf_name}/{time_string}/run.log`
    other files like checkpoint will be saved in the same folder
    """
    config_split_list = config_path.split("/")
    config_split_list[-1] = config_split_list[-1].replace(".yaml", "")
    now = datetime.now()
    time_string = now.strftime("%Y%m%d%H%M%S")
    log_path = "/".join([LOG_ROOT_PATH] + config_split_list[1:] + [time_string])
    os.makedirs(log_path, exist_ok=True)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_path, "run.log")),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return log_path, logger
