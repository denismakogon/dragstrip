#!/usr/bin/env python
import argparse
import logging
import sys
import time
import types

import eventlet
from oslo import messaging

from options import conf


logging.basicConfig()
eventlet.monkey_patch()


class OMClient(messaging.RPCClient):
    """Simple RPC client. It can be changed to do some delays or something like
    that.
    """
    def callA(self, context, args):
        self.call(context, 'methodA')

    def castB(self, context, args):
        self.cast(context, 'methodB', **args)


def _run(client, context, call_num):
    """The callback to spawn client green threads."""
    for i in range(0, call_num):
        print 'Client cast ', i
        client.castB(context, {})
        print 'Client call: ', i
        client.callA(context, {})


def _get_client(conf):
    transport_url = "rabbit://%(login)s:%(pass)s@%(host)s:%(port)s" % {
                    'login': conf.login,
                    'pass': conf.password,
                    'host': conf.transport_ip,
                    'port': conf.transport_port
                    }
    server_addr = "%s:%s" % (conf.server_ip, conf.server_port)

    transport = messaging.get_transport(cfg.CONF, url=transport_url)
    target = messaging.Target(topic='om-client', server=server_addr)
    return OMClient(transport, target)


def _spawn_threads(conf, client):
    test_context = {"application": "oslo.messenger-server",
                    "time": time.ctime(),
                    "cast": False}

    call_n = 0
    while call_n < conf.thread_num:
        call_n = call_n + 1
        yield eventlet.spawn(_run, client, test_context, conf.call_num)


def main():
    threads = list(_spawn_threads(conf, _get_client(conf)))
    try:
        for th in threads:
            th.wait()
    except KeyboardInterrupt:
        for th in threads:
            th.kill()
        print '<Ctrl>+c exit'
    except Exception as e:
        print e
        raise
    return 0


if __name__ == '__main__':
    sys.exit(main())
