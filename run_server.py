#!/usr/bin/env python
from cli_serv import server
import options


def run_server():
    conf = options.register_server_opts()

    serv = server.get_server(conf)
    try:
        serv.start()
        serv.wait()
    except KeyboardInterrupt:
        serv.stop()


if __name__ == '__main__':
    run_server()
