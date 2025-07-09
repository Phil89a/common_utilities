import os
import sys
from loguru import logger

class LoggerFactory:
    _configured = False

    @classmethod
    def configure(cls):
        if cls._configured:
            return

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_dir = os.getenv("LOG_DIR", "./logs")
        log_file = os.path.join(log_dir, "app.log")
        os.makedirs(log_dir, exist_ok=True)

        logger.remove()  # Remove default

        # Console formatter (local time, 20-char padded name)
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm}</green> - "
            "<cyan>{extra[name]:<20.20}</cyan> - "
            "<level>{message}</level>"
        )

        logger.add(
            sys.stdout,
            level=log_level,
            format=console_format,
            backtrace=False,
            diagnose=False
        )

        # JSON file logger using serialize=True
        logger.add(
            log_file,
            level=log_level,
            rotation="5 MB",
            retention=5,
            serialize=True,  # <-- handles JSON formatting automatically
        )

        cls._configured = True

    @staticmethod
    def get_logger(module_path: str):
        LoggerFactory.configure()

        # Shorten logger name for clarity (e.g., a.b.c → a.b.c)
        parts = module_path.split(".")
        short_name = ".".join([p[0] for p in parts[:-1]] + [parts[-1]]) if len(parts) > 1 else module_path

        return logger.bind(name=short_name)