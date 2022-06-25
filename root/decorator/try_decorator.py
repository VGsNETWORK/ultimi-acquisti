#!/usr/bin/env python3
import root.util.logger as logger


def try_catch(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("Unable to finish function {}".format(func.__name__))
            logger.error(e)

    return wrapper
