#!/usr/bin/env python
"""RabbitMQ oslo.messaging driver load testing tool server.
Usage.
------

Start the server before the client starting. The server prints used transport 
and server ips and ports at starting. Please use the taken from the server
starting output ips and ports to start the appropriate client arguments.

You can start server without args if your RabbitMQ env using the default
credentials and port.

"""

import argparse
import logging
import netifaces
import sys
import threading
import types
import uuid, time

import eventlet
from oslo.config import cfg
from oslo import messaging

from common import cred

logging.basicConfig()
eventlet.monkey_patch()

class Enpoint(object):
    """Simulated an application to be called from messaging."""

    def methodA(self, *args, **kwargs):
        print 'Method A is called on an end point'

    def methodB(self, *args, **kwargs):
        print 'Method B is called on an end point'


def main():
    parser = argparse.ArgumentParser()
    # Ports
    parser.add_argument('--serv_p', dest='server_port', default='5672')
    parser.add_argument('--trans_p', dest='transport_port',
        default=5672, type=types.IntType)
    # Credentials
    parser.add_argument('--l', dest='login', default='guest')
    parser.add_argument('--s', dest='password', default='guest')
    args = parser.parse_args()

    not_local = lambda x: x and not x.startswith('127')
    inet_addr = lambda x: x is not None and x[0]['addr']
    ifaces = lambda x: netifaces.ifaddresses(x).get(netifaces.AF_INET)

    # Get internal IP to start the server
    addr = filter(
        not_local, map(inet_addr, map(ifaces, netifaces.interfaces())))[0]

    transport_url = "rabbit://%(login)s:%(pass)s@%(host)s:%(port)s" % {
                    'login': args.login,
                    'pass': args.password,
                    'host': addr,
                    'port': args.transport_port
                    }

    transport = messaging.get_transport(cfg.CONF, url=transport_url)
    target = messaging.Target(topic='om-client', server=addr)
    endpoints = [Enpoint(), ]
    server = messaging.get_rpc_server(
        transport, target, endpoints, executor='eventlet')
    print "Starting server"
    try:
        server.start()
        server.wait()
    except KeyboardInterrupt:
        server.stop()
    print "Quitting ..."
    return 0


if __name__ == '__main__':
    sys.exit(main())
