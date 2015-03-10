from oslo.config import cfg


def _register_opts():
    conf = cfg.CONF
    opts = [cfg.StrOpt('server_ip', short="si"),
            cfg.IntOpt('server_port', short="sp"),
            cfg.StrOpt('transport_ip', short="ti"),
            cfg.IntOpt('transport_port', short="tp"),
            cfg.StrOpt('login', short="l"),
            cfg.StrOpt('password', short="p"),
            cfg.IntOpt('call_num', short="c"),
            cfg.IntOpt('thread_num', short="t"),
            cfg.ListOpt('foreign_nodes', short='fn'),
            cfg.StrOpt('plotly_name', short='pln'),
            cfg.StrOpt('plotly_api_key', short='plk'),
            cfg.BoolOpt('dynamic_charts', short='dc'),
            cfg.IntOpt('management_port', short="mp"),
            cfg.StrOpt('management_ip', short='ma')]

    conf.register_cli_opts(opts)
    conf(default_config_files=['rpc.conf'], )
    return conf


conf = _register_opts()
