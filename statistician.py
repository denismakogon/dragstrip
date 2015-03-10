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
import collections

import psutil
from plotly import graph_objs
from plotly import plotly

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
            print e
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
    url = "http://%s:%d/api/overview" % (conf.management_ip,
                                         conf.management_port)
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

    try:
        with open(file, 'r+') as file:
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


# =============================================================================
# Plotly handler
# =============================================================================
def get_timed(data, key):
    """Group logging data items by logging time."""

    items = [
        (k, v[key]) for k, v in data.items() if isinstance(v, types.DictType)]
    t_format = '%Y-%m-%d %H:%M:%S'
    items = sorted(items, cmp=lambda x, y: cmp(
        time.strptime(x[0], t_format),
        time.strptime(y[0], t_format)))
    try:
        timeline, values = zip(*[(i[0], i[1].items()) for i in items])
        values = [zip(*i) for i in zip(*values)]
        return timeline, [(i[0][0], i[1]) for i in values]
    except AttributeError:
        timeline, values = zip(*items)
        return (timeline,
                [('Core%d' % (i+1), v) for i, v in enumerate(zip(*values))])


def get_rabbit_plotly():
    """Get rabbit numeric data prepared for charts building with Plotly."""

    data = json.loads(get_rabbit_info())
    return {i: get_timed(data, i) for i in ('object_totals', 'queue_totals')}


def get_system_plotly():
    """Get system numeric data prepared for charts building with Plotly."""

    data = json.loads(get_system_info())
    return {k: {i: get_timed(v, i) for i in ('cpu','disk', 'ram')}\
                     for k, v in data.items()}


def build_chart(log, layout_title=''):
    """Buld plotly chart with given data."""

    time_series = log[0]
    data = graph_objs.Data([graph_objs.Scatter(x=time_series, y=v, name=name)\
                            for name, v in log[1]])
    layout = graph_objs.Layout(title=layout_title)
    figure = graph_objs.Figure(data=data, layout=layout)
    print plotly.plot(figure, filename='date-axes', fileopt='new')


def build_static_charts():
    """Iterate though a log data and build static charts with a given values"""

    plotly.sign_in(conf.plotly_name, conf.plotly_api_key)

    for host, logs in get_system_plotly().items():
        for name, log in logs.items():
            build_chart(log, '%s: %s' % (host, name))

    for name, log in get_rabbit_plotly().items():
        build_chart(log, name)


def dynamic_charts():
    # TODO: implement dynamic charts building.
    while True:
        break


# =============================================================================
# Run threads
# =============================================================================
def spawn(dynamic=False):
    pool = eventlet.greenpool.GreenPool(3)
    pool.spawn(run_logger)
    pool.spawn(run_http)
    if dynamic:
        pool.spawn(dynamic_charts, True)
    try:
        pool.waitall()
    except KeyboardInterrupt, SystemExit:
        build_static_charts()


if __name__ == '__main__':
    spawn()
