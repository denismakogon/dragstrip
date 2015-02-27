import datetime
import time
import re

from statistician import rabbit_log


RABBIT_LOG = 'rabbit.log'
SYSTEM_LOG = 'system.log'


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


def write_to_file(timekey, conf):
    """Write raw log data to a file."""

    logs = ((RABBIT_LOG, rabbit_log.get_rabbit_overview(conf)),
            (SYSTEM_LOG, rabbit_log.get_local_system_info(conf)))
    for file, log in logs:
        with open(file, 'a+') as o_file:
            o_file.write('"%s": %s\n' % (timekey, log))


def run_logger(conf):
    """Logging thread function."""

    while True:
        try:
            write_to_file(str(datetime.datetime.now().replace(microsecond=0)),
                          conf)
            time.sleep(3)
        except SystemExit, KeyboardInterrupt:
            break
