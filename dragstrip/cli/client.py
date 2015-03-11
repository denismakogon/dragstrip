import eventlet

from dragstrip.cli_serv import client
from dragstrip import options

eventlet.monkey_patch()


def run_client():
    conf = options.register_client_opts()

    inst_client = client.get_client(conf)
    pool = eventlet.greenpool.GreenPool(conf.thread_num)
    call_n = 0
    while call_n < conf.thread_num:
        call_n = call_n + 1
        pool.spawn(inst_client.run)
    try:
        pool.waitall()
    except KeyboardInterrupt:
        print "\nTerminated\n"
