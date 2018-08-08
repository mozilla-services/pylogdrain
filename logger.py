import logging
import os

log = logging.getLogger("logdrain")
log.setLevel(int(os.environ.get("LOGLEVEL", logging.INFO)))
