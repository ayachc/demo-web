import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "context=%(context)s | %(message)s"
)


class ContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "context"):
            record.context = "-"
        return True


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(ContextFilter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name):
    return logging.getLogger(name)
