#!/usr/bin/env python3

""" File with the logger class used by the various files """

import logging
import configparser
from os import environ


CONFIG = configparser.ConfigParser()
CONFIG.read("logger.conf")
FORMAT = "%(asctime)-15s %(levelname)s:%(funcName)-8s %(message)s"
FILE = "server.log"
LEVEL = logging.INFO
logging.basicConfig(filename=FILE, filemode="a", format=FORMAT, level=LEVEL)


def info(message: str):
    """Log a message of at level INFO

    Args:
        message ([str]): The message to log
    """
    logging.info(message)


def error(message: str):
    """Log a message of at level ERROR

    Args:
        message ([str]): The message to log
    """
    logging.error(message)


def warn(message: str):
    """Log a message of at level WARNING

    Args:
        message ([str]): The message to log
    """
    logging.warning(message)


def debug(message: str):
    """Log a message of at level DEBUG

    Args:
        message ([str]): The message to log
    """
    logging.debug(message)


def exception(exception: Exception):
    logging.exception(exception)
