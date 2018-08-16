import logging
import os


def getLevel():
    level = os.environ.get("LOGLEVEL", "INFO")
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARN":
        return logging.WARN

    return logging.INFO


log = logging.getLogger("logdrain")
log.setLevel(getLevel())
