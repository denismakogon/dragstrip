#!/usr/bin/env python
import argparse
import logging
import sys
import time
import types

from oslo import messaging

from dragstrip import options

class Client(messaging.RPCClient):
    _context = {"application": "oslo.messenger-server",
                "time": time.ctime(),
                "cast": False}

    def __init__(self, conf, *args, **kwargs):
        self.conf = conf
        super(Client, self).__init__(*args, **kwargs)

    def _call(self, context, args):
        self.call(self._context, 'method_a')

    def _cast(self, context, args):
        self.cast(self._context, 'method_b', **args)

    def run(self):
        """The callback to spawn client green threads."""

        call_num = self.conf.call_num
        cond = lambda x: x < call_num if call_num else lambda x: True
        i = 0
        while cond(i):
            print 'Client cast ', i
            self._cast(self._context, {})
            print 'Client call: ', i
            self._call(self._context, {})
            i = i + 1


def get_client(conf):
    transport_url = "rabbit://%(login)s:%(pass)s@%(host)s:%(port)s" % {
                    'login': conf.login,
                    'pass': conf.password,
                    'host': conf.transport_ip,
                    'port': conf.transport_port
                    }
    server_addr = "%s:%s" % (conf.server_ip, conf.server_port)

    transport = messaging.get_transport(conf, url=transport_url)
    target = messaging.Target(topic='om-client', server=server_addr)
    return Client(conf, transport, target)
