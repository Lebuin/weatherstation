from __future__ import annotations

import queue
import time
import typing
from dataclasses import dataclass
from datetime import datetime, timedelta

__all__ = (
    'scheduler',
)


@dataclass
class SchedulerItem:
    fn: typing.Callable
    execution_time: datetime
    args: tuple
    kwargs: dict

    def __lt__(self, other: SchedulerItem):
        return self.execution_time < other.execution_time


class Scheduler:
    queue: queue.PriorityQueue[SchedulerItem]


    def __init__(self):
        self.queue = queue.PriorityQueue()


    def delay(self, fn: typing.Callable, delay: timedelta, *args, **kwargs):
        execution_time = datetime.now() + delay
        item = SchedulerItem(fn, execution_time, args, kwargs)
        self.queue.put(item)


    def start_loop(self):
        try:
            self._loop()
        except queue.Empty:
            pass


    def _loop(self):
        while item:= self.queue.get():
            delay = item.execution_time - datetime.now()
            if delay > timedelta():
                time.sleep(delay.total_seconds())
            item.fn(*item.args, **item.kwargs)


scheduler = Scheduler()
