#!/usr/bin/env python
'''
Created on Dec 4, 2014

@author: ozamiatin
@co-authored Pekelny I159 Ilya
'''

import argparse
import logging
import sys
import time
import types

import eventlet
from oslo import messaging
from oslo.config import cfg

from common import cred

logging.basicConfig()
eventlet.monkey_patch()

class OMClient(messaging.RPCClient):
    def callA(self, context, args):
        self.call(context, 'methodA')

    def castB(self, context, args):
        self.cast(context, 'methodB', **args)


def run(client, context, call_num):
    for i in range(0, call_num):
        print 'Client cast ', i
        client.castB(context, {})
        print 'Client call: ', i
        client.callA(context, {})


def main():
    parser = argparse.ArgumentParser()

    # Call params
    parser.add_argument('--t', dest='threads_number',
        default=1, type=types.IntType)
    parser.add_argument('--c', dest='call_number',
        required=True, type=types.IntType)

    # Server and transport ips
    parser.add_argument('--serv_ip', dest='server_ip', default='127.0.0.1')
    parser.add_argument('--trans_p', dest='transport_port',
        default=5672, type=types.IntType)
    parser.add_argument('--trans_ip', dest='transport_ip', default='127.0.0.1')

    parser.add_argument('--l', dest='login', default='guest')
    parser.add_argument('--s', dest='password', default='guest')
    args = parser.parse_args()


    transport_url = "rabbit://%(login)s:%(pass)s@%(host)s:%(port)s" % {
                    'login': args.login,
                    'pass': args.password,
                    'host': args.transport_ip,
                    'port': args.transport_port
                    }
    transport = messaging.get_transport(cfg.CONF, url=transport_url)
    target = messaging.Target(topic='om-client', server=args.server_ip)
    client = OMClient(transport, target)

    test_context = {"application": "oslo.messenger-server",
                    "time": time.ctime(),
                    "cast": False}

    threads = [eventlet.spawn(
        run, client, test_context, args.call_number) for i in range(
            0, args.threads_number)]
    try:
        for i in threads:
            i.wait()
    except KeyboardInterrupt:
        for i in threads:
            i.kill()
        print 'Ctrl+C exit'
    except Exception as e:
        print e
        raise


    print 'Client Quitting ...'
    return 0


if __name__ == '__main__':
    sys.exit(main())
