import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os
import conf

logging.basicConfig()
LOGLEVEL = logging.WARNING
logging.getLogger('sqlalchemy.engine').setLevel(LOGLEVEL)
logging.getLogger("requests").setLevel(LOGLEVEL)
logging.getLogger("urllib3").setLevel(LOGLEVEL)

#LOGFORMAT = '[%(asctime)s] %(message)s'
LOGFORMAT = '[%(asctime)s] %(levelname)s %(module)s:%(lineno)d %(message)s'
BACKCOUNT = 15

LOGLEVEL = logging.INFO
alogger = logging.getLogger('action')
slogger = logging.getLogger('spider')
elogger = logging.getLogger('event')

logger_list = [alogger, slogger, elogger]

for l in logger_list:
    l.setLevel(LOGLEVEL)
    l.propagate = False

def init_logger(path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    global alogger, slogger, elogger

    for l in logger_list:
        if not l.handlers:
            handler = logging.handlers.TimedRotatingFileHandler('{}{}{}.log'.format(path, os.sep, l.name), when='midnight', interval=1, backupCount=BACKCOUNT)
            handler.setLevel(LOGLEVEL)
            formatter = logging.Formatter(LOGFORMAT)
            handler.setFormatter(formatter)
            l.addHandler(handler)

        if conf.DEBUG_MODE:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(LOGFORMAT)
            handler.setFormatter(formatter)
            l.addHandler(handler)

    #if not alogger.handlers:
    #    handler = logging.handlers.TimedRotatingFileHandler(path + os.sep + 'action.log', when='midnight', interval=1, backupCount=BACKCOUNT)
    #    handler.setLevel(LOGLEVEL)
    #    formatter = logging.Formatter(LOGFORMAT)
    #    handler.setFormatter(formatter)
    #    alogger.addHandler(handler)

    #if not slogger.handlers:
    #    handler = logging.handlers.TimedRotatingFileHandler(path + os.sep + 'spider.log', when='midnight', interval=1, backupCount=BACKCOUNT)
    #    handler.setLevel(LOGLEVEL)
    #    formatter = logging.Formatter(LOGFORMAT)
    #    handler.setFormatter(formatter)
    #    slogger.addHandler(handler)

    #if not elogger.handlers:
    #    handler = logging.handlers.TimedRotatingFileHandler(path + os.sep + 'event.log', when='midnight', interval=1, backupCount=BACKCOUNT)
    #    handler.setLevel(LOGLEVEL)
    #    formatter = logging.Formatter(LOGFORMAT)
    #    handler.setFormatter(formatter)
    #    elogger.addHandler(handler)


