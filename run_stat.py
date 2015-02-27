#!/usr/bin/env python
from statistician import log_utils
from statistician import sys_log
from statistician import plot
import eventlet
import options


def run_stat():
    conf = options.register_stat_opts()

    pool = eventlet.greenpool.GreenPool(3)
    pool.spawn(log_utils.run_logger, conf)
    pool.spawn(sys_log.run_http)
    if conf.dynamic_charts:
        pool.spawn(plot.dynamic_charts, True)
    try:
        pool.waitall()
    except KeyboardInterrupt:
        print "\nTerminated\n"


if __name__ == '__main__':
    run_stat()
