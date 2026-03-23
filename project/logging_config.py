import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(level=logging.INFO, log_file="app.log"):
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # # Console handler
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(formatter)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,  # 1MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    # Prevent duplicates
    # if not root_logger.handlers:
    #     root_logger.addHandler(console_handler)
    #     root_logger.addHandler(file_handler)

    # Silence noisy libs
    noisy_libs = ["apscheduler", "openweather", "openai", "httpx", "urllib3"]
    for lib in noisy_libs:
        logging.getLogger(lib).setLevel(logging.WARNING)