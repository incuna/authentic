from django.db import models
from django.conf import settings
from authentic.admin_log_view import views
from registration.signals import user_registered
from registration.signals import user_activated
import logging
from logging.handlers import SysLogHandler
import threading

_LOCAL = threading.local()

def getlogger():
    
    logger = getattr(_LOCAL, 'logger', None)
    if logger is not None:
        return logger
    logger = logging.getLogger()

    formatter = logging.Formatter('[%(asctime)s]%(levelname)-8s"%(message)s"','%Y-%m-%d %a %H:%M:%S') 
    
    log_handler = logging.FileHandler(settings.LOG_FILENAME)
    log_handler.setFormatter(formatter)
    log_handler.setLevel(settings.LOG_FILE_LEVEL)
    logger.addHandler(log_handler)
    
    if settings.LOG_SYSLOG:
        syslog_handler = SysLogHandler(address = '/dev/log')
        formatter = logging.Formatter('authentic %(levelname)-8s"%(message)s"','%Y-%m-%d %a %H:%M:%S') 
        syslog_handler.setFormatter(formatter)
        syslog_handler.setLevel(settings.LOG_SYS_LEVEL)
        logger.addHandler(syslog_handler)
    
    setattr(_LOCAL,'logger',logger)
    return logger

def debug(msg):
    logger = getlogger()
    logger.debug(msg)

def info(msg):
    logger = getlogger()
    logger.info(msg)

def critical(msg):
    logger = getlogger()
    logger.critical(msg)

def warning(msg):
    logger = getlogger()
    logger.warning(msg)

def error(msg):
    logger = getlogger()
    logger.error(msg)

def LogRegistered(sender, user, **kwargs):
    msg = user.username + ' is now registered'
    info(msg)

def LogActivated(sender, user, **kwargs):
    msg = user.username + ' has activated his acount'
    info(msg)

user_registered.connect(LogRegistered, dispatch_uid = "authentic.admin_log_view")
user_activated.connect(LogActivated, dispatch_uid = "authentic.admin_log_view")

class Log(models.Model):
    pass

# Create your models here.
