#!/usr/bin/env python3

""" Custom class for Background Process """

from multiprocessing import Process, Event


class CProcess(Process):
    """Custom implementation of Process class to store target and args"""

    def __init__(
        self, target: callable, group: str = "", name: str = "", args: tuple = ()
    ):
        super().__init__(group=group, target=target, args=args, name=name)
        self.target = target
        self.args = args
        self.exit = Event()

    def shutdown(self):
        """shutdown process"""
        self._popen.terminate()
        self._popen.kill()
        self.exit.set()
