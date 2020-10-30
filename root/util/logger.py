#!/usr/bin/env python3

import logging
import configparser

""" File with the logger class used by the various files """


class Logger:
    """ Class used to log messages in a file """

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read("logger.conf")
        self._format = "%(asctime)-15s %(levelname)s:%(funcName)-8s %(message)s"
        self._file = "server.log"
        self._level = logging.INFO
        logging.basicConfig(
            filename=self._file, filemode="a", format=self._format, level=self._level
        )

    def info(self, message: str):
        """Log a message of at level INFO

        Args:
            message ([str]): The message to log
        """
        logging.info(message)

    def error(self, message: str):
        """Log a message of at level ERROR

        Args:
            message ([str]): The message to log
        """
        logging.error(message)

    def warn(self, message: str):
        """Log a message of at level WARNING

        Args:
            message ([str]): The message to log
        """
        logging.warn(message)

    def debug(self, message: str):
        """Log a message of at level DEBUG

        Args:
            message ([str]): The message to log
        """
        logging.debug(message)
