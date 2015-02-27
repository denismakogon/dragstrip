DRAGSTRIP
=========

Load testing tool for oslo.messaging. RabbitMQ transport specific
(at least for now.)

### Usage

First of all you have to prepare a Rabbit cluster with enabled management
plugin.
* https://www.rabbitmq.com/clustering.html
* https://www.rabbitmq.com/management.html

After you should register an account on http://plot.ly

Dragstrip uses single config file to configure the app - `rpc.conf`. All the
dynamic options you can redefine though shell options.

- server_ip si: ip address of the machine runs server script, default is localhost
- server_port sp: a port listened by a rabbitmq server
- transport_ip ti: rabbitmq transport port, usually the same as a server ip
- transport_port tp: rabbitmq transport port, usually the same as a server port
- login l: login for rabbitmq cluster management api
- password p:password for rabbitmq management api
- management_port mp:a port used by rabbitmq managment plugin.
- call_num c: number of client calls per thread (client specific option)
- thread_num t: number of a client threads.
- foreign_nodes fn: list of cluster nodes ips. Logger specific option. Required for system statistics collecting.
- plotly_name pln: name of your plot.ly account
- plotly_api_key plk:plot.ly api key. You can get it from plot.ly/settings
- dynamic_charts dc: if true all the charts will be builded dynamically during testing process. Not implemented yet.

Dragstrip contains three entities: client, server and statistician. Start client
and server with corresponding options passed from a local custom rpc.conf or as
a shell opts. Start a statistician instance on a node comprised in a RabbitMQ cluster.
Static plots will be builded only at statistician instance termination. Statistician
script collects overall Rabbitmq cluster transport specific statistic and
system statistic from a single instance.
