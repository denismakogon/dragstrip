from distutils.core import setup


setup(name='dragstrip',
      version='0.1',
      url='https://github.com/I159/dragstrip',
      author='Pekelny Ilya',
      author_email='pekelny@gmail.com',
      description='RabbitMQ oslo.messaging driver load testing tool.',

      packages=['dragstrip', 'dragstrip.cli_serv', 'dragstrip.statistician'],
      package_dir={'dragstrip': 'dragstrip'},
      scripts=['dragstrip/drag_client', 'dragstrip/drag_server',
               'dragstrip/drag_stat'],
      install_requires=['oslo.messaging>=1.4.0', 'eventlet>=0.16.1',
                        'oslo.config>=1.9.0', 'psutil>=2.2.1',
                        'plotly>=1.6.6', 'netifaces>=0.10.4', 'httplib2>=0.9'],
      package_data={'dragstrip': ['rpc.conf', ]})
