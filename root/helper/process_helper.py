#!/usr/bin/env python3

from mult/iprocessing import Process, active_children
from root.util.logger import Logger

PROCESS_NAME = "ultimi_acquisti_process_%s"

logger = Logger()

def find_process(name_prefix: str) -> Process:
    for process in active_children():
        title = PROCESS_NAME % name_prefix
        if title == process.name:
            return process
    return None


def restart_process(message_id: int) -> None:
    process: Process = find_process(str(message_id))
    if not process:
        logger.warning(f"Unable to find the process with name {PROCESS_NAME % process}")
        return
    target = process.target
    args = process.args
    process.terminate()
    create_process(str(message_id), target, args)


def create_process(name_prefix: str, target: function, args: tuple) -> None:
    process: Process = Process(target=target, args=args)
    process.name = PROCESS_NAME % name_prefix
    process.start()
