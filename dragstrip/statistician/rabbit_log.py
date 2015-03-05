import urllib2

import httplib2

from statistician import log_utils


def get_rabbit_overview(conf):
    """Get rabbitmq cluster overview."""

    requester = httplib2.Http(".cache")
    requester.add_credentials(name=conf.login, password=conf.password)
    url = "http://%s:%d/api/overview" % (conf.transport_ip,
                                         conf.management_port)
    resp, content = requester.request(
        url, "GET", headers={'content-type': 'application/json'})
    if resp.status != 200:
        raise urllib2.HTTPError(resp.status)
    return content


def get_rabbit_info():
    return log_utils.as_json(log_utilsRABBIT_LOG)