import BaseHTTPServer
import json
import types
import socket
import time

import psutil
import httplib2

from dragstrip.statistician import log_utils


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


def get_foreign_system_info(conf):
    """Parse system indicators from others nodes."""

    requester = httplib2.Http(".cache")
    logs = {}
    for i in conf.foreign_nodes:
        try:
            resp, content = requester.request("http://%s:8080" % i, "GET")
        except socket.error as e:
            print e
            time.sleep(3)
            return get_foreign_system_info(conf)
        if int(resp['status']) != 200:
            raise httplib2.ServerNotFoundError(i)
        logs[i] = json.loads(content)
    return logs


def get_system_info(conf):
    """Aggregate system information from all the cluster."""

    sys_log = get_foreign_system_info(conf)
    sys_log['localhost'] = json.loads(log_utils.as_json(log_utils.SYSTEM_LOG))
    return json.dumps(sys_log)


class SysLogHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Simple http server to share system information between nodes."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(log_utils.as_json(log_utils.SYSTEM_LOG))


def run_http():
    """Run the http server and share system information."""

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(('127.0.0.1', 8080), SysLogHandler)
    try:
        httpd.serve_forever()
    except (SystemExit, KeyboardInterrupt):
        httpd.server_close()
