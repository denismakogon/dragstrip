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
from oslo.config import cfg
from oslo import messaging


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


def _register_opts(conf):
    opts = [cfg.StrOpt('server_ip', short="si", default=_get_public_ip()),
            cfg.IntOpt('server_port', short="sp"),
            cfg.StrOpt('transport_ip', short="ti", default=_get_public_ip()),
            cfg.IntOpt('transport_port', short="tp"),
            cfg.StrOpt('login', short="l"),
            cfg.StrOpt('password', short="p")]
    conf.register_cli_opts(opts)
    conf(default_config_files=['rpc.conf', ])
    return conf


def _get_server(conf):
    transport_url = "rabbit://%(login)s:%(pass)s@%(host)s:%(port)s" % {
                    'login': conf.login,
                    'pass': conf.password,
                    'host': conf.transport_ip,
                    'port': conf.transport_port
                    }
    server_url = "%s:%s" % (conf.server_ip, conf.server_port)

    transport = messaging.get_transport(cfg.CONF, url=transport_url)
    target = messaging.Target(topic='om-client', server=server_url)
    endpoints = [Enpoint(), ]
    return messaging.get_rpc_server(
        transport, target, endpoints, executor='eventlet')


def main():
    conf = _register_opts(cfg.CONF)
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
