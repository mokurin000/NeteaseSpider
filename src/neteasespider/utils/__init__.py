from datetime import datetime
from time import sleep
from typing import Callable


def fit_qps(qps: int, func: Callable) -> Callable:
    prev = datetime.now().second
    result = func()

    to_sleep = (1 / qps) - (datetime.now().second - prev)
    if to_sleep > 0:
        sleep(to_sleep)

    return result
