#!/usr/bin/env python3

""" Custom class for Background Process """

from multiprocessing import Process


class CProcess(Process):
    """Custom implementation of Process class to store target and args"""

    def __init__(
        self, target: callable, group: str = "", name: str = "", args: tuple = ()
    ):
        super().__init__(group=group, target=target, args=args, name=name)
        self.target = target
        self.args = args
