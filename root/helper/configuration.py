#!/usr/bin/env python3

""" File used to manage the bot configurations """

import os
from mongoengine import DoesNotExist
from pymongo.errors import OperationFailure
from root.model.configuration import Configuration
from root.util.logger import Logger
from root.util.telegram import TelegramSender


class ConfigurationHelper:
    """ Class to manage the bot configurations """

    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()

    def load_configurations(self) -> None:
        """ Load configuration from the database """
        self.logger.info("loading configurations from database")
        try:
            configurations = Configuration.objects()
        except OperationFailure:
            configurations = []
        for configuration in configurations:
            os.system(f'export {configuration.code}="{configuration.value}"')
            os.environ[configuration.code] = configuration.value

    def update_configuration(self, code: str, value: str) -> None:
        """Update Configuration on the databae

        Args:
            code ([str]): The key of the row to update
            value ([str]): The new value
        """
        self.logger.info(f"updating configuration {code}")
        try:
            configuration = Configuration.objects().get(code=code)
            configuration.value = value
            configuration.save()
            self.logger.info("updated succesfully")
        except DoesNotExist:
            self.logger.warn("configuration not found, creating it")
            Configuration(code=code, value=value).save()
