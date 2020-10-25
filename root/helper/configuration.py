#!/usr/bin/env python3


import os
from mongoengine import DoesNotExist
from pymongo.errors import OperationFailure
from root.model.configuration import Configuration
from root.util.logger import Logger
from root.util.telegram import TelegramSender


class ConfigurationHelper:
    def __init__(self):
        self.logger = Logger()
        self.sender = TelegramSender()

    def load_configurations(self):
        self.logger.info("loading configurations from database")
        try:
            configurations = Configuration.objects()
        except OperationFailure:
            configurations = []
        except Exception as e:
            self.logger.error(e)
            configurations = []
        for configuration in configurations:
            os.system(f'export {configuration.code}="{configuration.value}"')
            os.environ[configuration.code] = configuration.value

    def update_configuration(self, code, value):
        self.logger.info(f"updating configuration {code}")
        try:
            configuration = Configuration.objects().get(code=code)
            configuration.value = value
            configuration.save()
            self.logger.info("updated succesfully")
        except DoesNotExist:
            self.logger.warn("configuration not found, creating it")
            Configuration(code=code, value=value).save()
