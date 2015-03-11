from dragstrip.cli_serv import server
from dragstrip import options


def run_server():
    conf = options.register_server_opts()

    serv = server.get_server(conf)
    try:
        serv.start()
        serv.wait()
    except KeyboardInterrupt:
        serv.stop()
