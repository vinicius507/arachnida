import logging


class ColoredFormatter(logging.Formatter):
    grey = "\x1b[38m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "DEBUG" + reset,
        logging.INFO: green + "INFO" + reset,
        logging.WARNING: yellow + "WARN" + reset,
        logging.ERROR: red + "ERROR" + reset,
        logging.CRITICAL: bold_red + "CRIT" + reset,
    }

    def format(self, record):
        log_fmt = "{level}: %(name)s: %(message)s"
        log_fmt = log_fmt.format(
            level=self.FORMATS.get(record.levelno, self.FORMATS[logging.DEBUG])
        )
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
