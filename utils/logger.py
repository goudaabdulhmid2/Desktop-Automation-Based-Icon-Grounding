import logging
import sys
from pathlib import Path
from datetime import datetime
import config


def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Name of the logger (usually __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = config.LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Formatter
        formatter = logging.Formatter(config.LOG_FORMAT)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger


def setup_file_logger(name: str, log_file: Path = None, level: str = None) -> logging.Logger:
    """
    Set up a logger that writes to both console and file.
    
    Args:
        name: Name of the logger
        log_file: Path to log file (default: logs/automation_YYYYMMDD_HHMMSS.log)
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = config.LOG_LEVEL
    
    logger = setup_logger(name, level)
    
    # File handler
    if log_file is None:
        logs_dir = config.PROJECT_ROOT / "logs"
        logs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f"automation_{timestamp}.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger


class LoggerMixin:
    """
    Mixin class to add logger property to any class.
    Usage: class MyClass(LoggerMixin): ...
    """
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger


if __name__ == "__main__":
    # Test logging
    logger = setup_logger(__name__, "DEBUG")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Test file logger
    file_logger = setup_file_logger("test", level="INFO")
    file_logger.info("This goes to both console and file")
