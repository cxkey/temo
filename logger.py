import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os
import conf

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

#LOGFORMAT = '[%(asctime)s] %(message)s'
LOGFORMAT = '[%(asctime)s] %(levelname)s %(module)s:%(lineno)d %(message)s'
LOGLEVEL = logging.DEBUG
BACKCOUNT = 15

alogger = logging.getLogger('')
alogger.setLevel(LOGLEVEL)
alogger.propagate = False

elogger = logging.getLogger('event')
elogger.setLevel(LOGLEVEL)
elogger.propagate = False

def init_logger(path):
    if not os.path.exists(path):
        os.makedirs(path)

    global alogger, elogger

    if not alogger.handlers:
        handler = logging.handlers.TimedRotatingFileHandler(path + os.sep + 'action.log', when='midnight', interval=1, backupCount=BACKCOUNT)
        handler.setLevel(LOGLEVEL)
        formatter = logging.Formatter(LOGFORMAT)
        handler.setFormatter(formatter)
        alogger.addHandler(handler)

    if not elogger.handlers:
        handler = logging.handlers.TimedRotatingFileHandler(path + os.sep + 'event.log', when='midnight', interval=1, backupCount=BACKCOUNT)
        handler.setLevel(LOGLEVEL)
        formatter = logging.Formatter(LOGFORMAT)
        handler.setFormatter(formatter)
        elogger.addHandler(handler)

    if conf.DEBUG_MODE:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(LOGFORMAT)
        handler.setFormatter(formatter)
        alogger.addHandler(handler)

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(LOGFORMAT)
        handler.setFormatter(formatter)
        elogger.addHandler(handler)

