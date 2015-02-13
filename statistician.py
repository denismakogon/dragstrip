#!/usr/bin/env python

import datetime
import httplib2
import urllib2
import json
import pprint
import types

import psutil

from options import conf


LOG = {"Rabbit Info": {},
       "System Info": {}}


# TODO: Make simple REST http service to share system info.


def _is_pub_num(obj, key):
    if not key.startswith('_'):
        val = getattr(obj, key)
        return isinstance(val,(types.LongType, types.IntType, types.FloatType))
    return False


def _as_dict(obj):
    return {k: getattr(obj, k) for k in dir(obj) if _is_pub_num(obj, k)}


def add_rabbit_overview(conf):
    requester = httplib2.Http(".cache")
    requester.add_credentials(name=conf.login, password=conf.password)
    url = "http://%s:%d/api/overview" % (conf.transport_ip, conf.management_port)
    resp, content = requester.request(
        url, "GET", headers={'content-type': 'application/json'})
    if resp.status != 200:
        raise urllib2.HTTPError(resp.status)
    global LOG
    LOG['Rabbit Info'][str(datetime.datetime.now())] = json.loads(content)
    return LOG


def add_system_info():
    disk = psutil.disk_usage('/')
    swap = psutil.swap_memory()
    ram = psutil.phymem_usage()
    log = dict(swap=_as_dict(swap), ram=_as_dict(ram), disk=_as_dict(disk),
        cpu=psutil.cpu_percent(interval=1, percpu=True))
    global LOG
    LOG['System Info'][str(datetime.datetime.now())] = log
    return LOG


def write_to_file(log, file):
    readable = pprint.pformat(log)
    with open(file, 'a+') as o_file:
        o_file.write(readable)


# TODO: run on separate thread.
def run():
    add_rabbit_overview(conf)
    add_system_info()
    # TODO: write on termination
    write_to_file(LOG, 'load_test.log')
