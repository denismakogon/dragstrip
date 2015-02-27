#!/usr/bin/env python
import argparse
import logging
import sys
import time
import types

from oslo import messaging

import options

class Client(messaging.RPCClient):
    """Simple RPC client. It can be changed to do some delays or something like
    that.
    """

    _context = {"application": "oslo.messenger-server",
               "time": time.ctime(),
               "cast": False}

    def __init__(self, conf, *args, **kwargs):
        self.conf = conf
        super(Client, self).__init__(*args, **kwargs)

    def _call(self, context, args):
        self.call(self._context, 'Call method')

    def _cast(self, context, args):
        self.cast(self._context, 'Cast method', **args)

    def run(self):
        """The callback to spawn client green threads."""

        for i in range(0, self.conf.call_num):
            print 'Client cast ', i
            self._cast(self._context, {})
            print 'Client call: ', i
            self._call(self._context, {})


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
