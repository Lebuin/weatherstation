from __future__ import annotations

import logging
import sys
import time

from . import config
from .controller import Controller
from .graceful_killer import GracefulKiller

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

killer = GracefulKiller()

controller = Controller()


def run():
    loop()


def loop():
    while True:
        time.sleep(config.TICK_INTERVAL.total_seconds())

        # This doesn't work yet. Our script never seems to receive the SIGTERM signal that docker sends
        # when it wants the container to shut down. Not sure why, we need to investigate this.
        if killer.kill_now:
            break

        controller.tick()
