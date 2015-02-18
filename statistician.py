#!/usr/bin/env python

import datetime
import httplib2
import urllib2
import json
import pprint
import types
import time
import BaseHTTPServer
import eventlet
import socket
import re

import psutil

from options import conf


RABBIT_LOG = 'rabbit.log'
SYSTEM_LOG = 'system.log'


eventlet.monkey_patch()

# =============================================================================
# System indicators
# =============================================================================
def _is_pub_num(obj, key):
    """Filter payload from psutil object to dump JSON."""

    if not key.startswith('_'):
        val = getattr(obj, key)
        return isinstance(val,(types.LongType, types.IntType, types.FloatType))
    return False


def _ps_to_dict(obj):
    """Convert psutil object to ditct of payload values to dump JSON."""

    return {k: getattr(obj, k) for k in dir(obj) if _is_pub_num(obj, k)}


def get_local_system_info():
    """Get system indicators from a local OS."""

    disk = psutil.disk_usage('/')
    swap = psutil.swap_memory()
    ram = psutil.phymem_usage()
    return json.dumps(dict(swap=_ps_to_dict(swap),
                           ram=_ps_to_dict(ram),
                           disk=_ps_to_dict(disk),
                           cpu=psutil.cpu_percent(interval=1, percpu=True)))


def get_foreign_system_info():
    """Parse system indicators from others nodes."""

    requester = httplib2.Http(".cache")
    logs = {}
    for i in conf.foreign_nodes:
        try:
            resp, content = requester.request("http://%s:8080" % i, "GET")
        except socket.error as e:
            time.sleep(3)
            return get_foreign_system_info()
        if int(resp['status']) != 200:
            raise httplib2.ServerNotFoundError(i)
        logs[i] = json.loads(content)
    return logs


def get_system_info():
    """Aggregate system information from all the cluster."""

    sys_log = get_foreign_system_info()
    sys_log['localhost'] = json.loads(as_json(SYSTEM_LOG))
    return json.dumps(sys_log)


class SysLogHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Simple http server to share system information between nodes."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(as_json(SYSTEM_LOG))


def run_http():
    """Run the http server and share system information."""

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(('127.0.0.1', 8080), SysLogHandler)
    try:
        httpd.serve_forever()
    except (SystemExit, KeyboardInterrupt):
        httpd.server_close()


# =============================================================================
# Rabbit information
# =============================================================================
def get_rabbit_overview(conf):
    """Get rabbitmq cluster overview."""

    requester = httplib2.Http(".cache")
    requester.add_credentials(name=conf.login, password=conf.password)
    url = "http://%s:%d/api/overview" % (conf.transport_ip, conf.management_port)
    resp, content = requester.request(
        url, "GET", headers={'content-type': 'application/json'})
    if resp.status != 200:
        raise urllib2.HTTPError(resp.status)
    return content


def get_rabbit_info():
    """Alias for api uniformity."""
    return as_json(RABBIT_LOG)


# =============================================================================
# Logging
# =============================================================================
def as_json(file):
    """Open log file and convert a given content to a valid JSON object."""

    with open(file, 'r') as file:
        try:
            json_obj = "{%s}" % ', '.join(file.readlines())
            json_obj = json_obj.replace('\n', '')
            json_obj = json_obj.replace("'", '"')
            json_obj = re.sub('\d+(L)', '', json_obj)
            return json_obj
        except IOError:
            time.sleep(3)
            return as_json(file)


def write_to_file(timekey):
    """Write raw log data to a file."""

    logs = ((RABBIT_LOG, get_rabbit_overview(conf)),
            (SYSTEM_LOG, get_local_system_info()))
    for file, log in logs:
        with open(file, 'a+') as o_file:
            o_file.write('"%s": %s\n' % (timekey, log))


def run_logger():
    """Logging thread function."""

    while True:
        try:
            write_to_file(str(datetime.datetime.now().replace(microsecond=0)))
            time.sleep(3)
        except SystemExit, KeyboardInterrupt:
            break



def run_handler():
    while True:
        try:
            time.sleep(3)
            system = get_system_info()
            rabbit = get_rabbit_info()
# TODO: implement JSON parser to get plotly valid data.
# TODO: implement plotly worker.
        except SystemExit, KeyboardInterrupt:
            break
        except IOError:
            print "Log files haven't been generated. Retrying."
            continue


# TODO: run from client and server.
def spawn():
    pool = eventlet.greenpool.GreenPool(3)
    pool.spawn(run_handler)
    pool.spawn(run_http)
    pool.spawn(run_logger)
    pool.waitall()


if __name__ == '__main__':
    spawn()
