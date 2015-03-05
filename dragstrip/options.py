import os.path

from oslo.config import cfg


CONF = cfg.CONF


def register(f):
    """Register options and parse options file."""

    def wrap():
        cli_opts, opts = f()

        cli_opts = [cfg.StrOpt('server_ip', short="si"),
                    cfg.IntOpt('server_port', short="sp"),
                    cfg.StrOpt('transport_ip', short="ti"),
                    cfg.IntOpt('transport_port', short="tp")] + cli_opts

        opts = [cfg.StrOpt('login', short="l"),
                cfg.StrOpt('password', short="p")] + opts

        CONF.register_cli_opts(cli_opts)
        CONF.register_opts(opts)
        CONF(default_config_files=[
            os.path.join(os.path.dirname(__file__), 'rpc.conf'), ])
        return CONF
    return wrap



@register
def register_server_opts():
    # NOTE: server has no specific options, but it could be added with feature
    # features. This function is needed for the interface uniformity.
    return ([], [])


@register
def register_client_opts():
    return ([cfg.IntOpt('call_num', short="c"),
             cfg.IntOpt('thread_num', short="t")],
            [])


@register
def register_stat_opts():
    return ([cfg.BoolOpt('dynamic_charts', short='dc'),
             cfg.IntOpt('management_port', short="mp"),
             cfg.StrOpt('management_ip', short='ma')],
            [cfg.ListOpt('foreign_nodes', short='fn'),
             cfg.StrOpt('plotly_name', short='pln'),
             cfg.StrOpt('plotly_api_key', short='plk')])
