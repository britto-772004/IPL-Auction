import logging
import queue

import logging_loki

from backend.config.env_config import settings

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root_logger.addHandler(console_handler)

    loki_handler = logging_loki.LokiQueueHandler(
        queue.Queue(-1),
        url=settings.loki_url,
        tags={"service": "backend"},
        version="1",
    )
    root_logger.addHandler(loki_handler)
