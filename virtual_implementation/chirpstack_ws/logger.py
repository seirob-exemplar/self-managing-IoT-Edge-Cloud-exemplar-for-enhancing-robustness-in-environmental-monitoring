import logging
import pathlib
import os
from logging.handlers import RotatingFileHandler


PROJECT_PATH = pathlib.Path(__file__).parent.resolve().as_posix()
PATH_LOG = PROJECT_PATH + "/log"

def getLogger(filename:str=""):
    logFile = PATH_LOG + "/" + filename
    
    if not os.path.exists(PATH_LOG):
        os.makedirs(PATH_LOG)
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt="%d/%m/%Y %H:%M:%S")
    writeLog = logging.getLogger(filename)

    if writeLog.hasHandlers():
        return writeLog

    writeLog.setLevel(logging.INFO)
    handler = RotatingFileHandler(logFile, maxBytes=2*1024*1024, backupCount=7) 
    handler.setFormatter(log_formatter)
    writeLog.addHandler(handler)
    
    return writeLog
