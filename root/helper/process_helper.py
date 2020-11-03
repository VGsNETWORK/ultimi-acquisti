#!/usr/bin/env python3

from multiprocessing import Process, active_children
from root.util.logger import Logger

PROCESS_NAME = "ultimi_acquisti_process_%s"

logger = Logger()

def find_process(name_prefix: str) -> Process:
    """Retrieve a process using a prefix name as a key

    Args:
        name_prefix (str): The name prefix used to identify the process

    Returns:
        Process: The found process or None if nothing
    """
    for process in active_children():
        title = PROCESS_NAME % name_prefix
        if title == process.name:
            return process
    return None


def restart_process(key: str) -> None:
    """Restart a background process identified by a key

    Args:
        key (str): The identifier of the process
    """
    key = str(key)
    process: Process = find_process(key)
    if not process:
        logger.warn(f"Unable to find the process with name {PROCESS_NAME % key}")
        return
    target = process.target
    args = process.args
    process.terminate()
    create_process(key, target, args)


def create_process(name_prefix: str, target: callable, args: tuple) -> None:
    """Create a new background process and start it

    Args:
        name_prefix (str): The name prefix used to identify the process
        target (callable): The target to execute by the process
        args (tuple): The arguments to pass to the target
    """
    name: str = PROCESS_NAME % name_prefix
    process: Process = Process(target=target, args=args, name=name)
    process.start()
