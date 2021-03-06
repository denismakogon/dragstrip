#!/usr/bin/env python

import argparse
import logging
import json
import netifaces
import sys
import threading
import types
import uuid, time

import eventlet
from oslo import messaging
from oslo.config import cfg

import options


logging.basicConfig()
eventlet.monkey_patch()


class Enpoint(object):
    """Simulated an application to be called from messaging."""

    def methodA(self, *args, **kwargs):
        print 'Method A is called on an end point'

    def methodB(self, *args, **kwargs):
        print 'Method B is called on an end point'


def _get_public_ip():
    not_local = lambda x: x and not x.startswith('127')
    inet_addr = lambda x: x is not None and x[0]['addr']
    ifaces = lambda x: netifaces.ifaddresses(x).get(netifaces.AF_INET)

    return filter(
        not_local, map(inet_addr, map(ifaces, netifaces.interfaces())))[0]


def _set_opts(conf):
    opts = conf._opts['server_ip']['opt'], conf._opts['server_ip']['opt']
    local_ip = _get_public_ip()
    cfg.set_defaults(opts, server_ip=local_ip, transport_ip=local_ip)
    return conf


def _get_server(conf):
    transport_url = "rabbit://%(login)s:%(pass)s@%(host)s:%(port)s" % {
                    'login': conf.login,
                    'pass': conf.password,
                    'host': conf.transport_ip,
                    'port': conf.transport_port
                    }
    server_url = "%s:%s" % (conf.server_ip, conf.server_port)

    transport = messaging.get_transport(conf, url=transport_url)
    target = messaging.Target(topic='om-client', server=server_url)
    endpoints = [Enpoint(), ]
    return messaging.get_rpc_server(
        transport, target, endpoints, executor='eventlet')


def main():
    conf = _set_opts(options.conf)
    server = _get_server(conf)

    print "Starting server"
    print (
        "Please, use %s as client --serv_ip, and %s as client --serv_p values"
        ) % (conf.server_ip, conf.server_port)
    try:
        server.start()
        server.wait()
    except KeyboardInterrupt:
        server.stop()
    print "Quitting ..."
    return 0


if __name__ == '__main__':
    sys.exit(main())
