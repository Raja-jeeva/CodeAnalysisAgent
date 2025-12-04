import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "output")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

_handler = RotatingFileHandler(LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=2)
_handler.setFormatter(_formatter)
_handler.setLevel(logging.INFO)

_root_logger = logging.getLogger("requirements_verifier")
if not _root_logger.handlers:
    _root_logger.setLevel(logging.INFO)
    _root_logger.addHandler(_handler)

def get_logger(name: str) -> logging.Logger:
    logger = _root_logger.getChild(name)
    return logger
