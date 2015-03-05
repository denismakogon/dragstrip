import json
import time
import types

from plotly import graph_objs
from plotly import plotly


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
