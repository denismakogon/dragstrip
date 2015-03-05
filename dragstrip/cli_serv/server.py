#!/usr/bin/env python

import argparse
import json
import logging
import netifaces
import sys
import types
import uuid, time

from oslo import messaging
from oslo.config import cfg

from dragstrip import options


logging.basicConfig()


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
    override = _get_public_ip()
    conf.set_override(name='server_ip', override=override)
    conf.set_override(name='transport_ip', override=override)
    return conf


def get_server(conf):
    conf = _set_opts(conf)
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
