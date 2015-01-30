#!/usr/bin/env python
'''
Created on Dec 1, 2014

@author: ozamiatin
@co-authored Pekelny I159 Ilya

Server
'''

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

    def methodA(self, *args, **kwargs):
        print 'Method A is called on an end point'

    def methodB(self, *args, **kwargs):
        print 'Method B is called on an end point'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serv_p', dest='server_port', default='5672')
    parser.add_argument('--trans_p', dest='transport_port',
        default=5672, type=types.IntType)

    parser.add_argument('--l', dest='login', default='guest')
    parser.add_argument('--s', dest='password', default='guest')
    args = parser.parse_args()

    not_local = lambda x: x and not x.startswith('127')
    inet_addr = lambda x: x is not None and x[0]['addr']
    ifaces = lambda x: netifaces.ifaddresses(x).get(netifaces.AF_INET)

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
