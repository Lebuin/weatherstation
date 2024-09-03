from __future__ import annotations

import logging
import sys
import time

from . import config
from .controller import Controller
from .graceful_killer import GracefulKiller

logging.basicConfig(
    stream=sys.stdout,
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

killer = GracefulKiller()

controller = Controller()


def run():
    loop()


def loop():
    while True:
        time.sleep(config.TICK_INTERVAL.total_seconds())

        if killer.kill_now:
            break

        controller.tick()
