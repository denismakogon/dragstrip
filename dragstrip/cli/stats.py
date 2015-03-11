import eventlet

from dragstrip import options
from dragstrip.statistician import log_utils
from dragstrip.statistician import sys_log
from dragstrip.statistician import plot


eventlet.monkey_patch()


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