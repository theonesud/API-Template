import os
import sys
from datetime import datetime, time

from loguru import logger

# from core.slack import send_error_to_slack, send_info_to_slack


def setup_logger(log_folder="logs", settings=None):
    # Remove default logger
    logger.remove()

    # Configure file logging
    os.makedirs(log_folder, exist_ok=True)
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = os.path.join(log_folder, f"app_{current_date}.log")

    # Add file handler
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=time(0, 0, 0),
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    # Add console handler with detailed exception formatting
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        level="ERROR",
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        backtrace=True,
        diagnose=True,
    )

    # try:
    #     logger.add(
    #         send_info_to_slack,
    #         format="{message}",
    #         filter=lambda record: record["level"].name == "INFO",
    #         level="INFO",
    #     )
    #     logger.add(
    #         send_error_to_slack,
    #         format="{message}",
    #         filter=lambda record: record["level"].no >= logger.level("ERROR").no,
    #         level="ERROR",
    #     )
    # except Exception as e:
    #     print(f"Error setting up Slack logging: {str(e)}")

    # Create and return the app_logger
    app_logger = logger.bind(time=lambda _: datetime.utcnow().time())
    return app_logger
