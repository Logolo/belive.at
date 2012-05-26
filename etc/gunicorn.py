import logging
import os
import signal
import sys

def post_fork(server, worker):
    import gevent_psycopg2
    gevent_psycopg2.monkey_patch()


max_requests = 20000
preload_app = False
timeout = 40
loglevel = 'warn'
worker_class = 'socketio.sgunicorn.GeventSocketIOWorker'
workers = 3

accesslog = 'serve.out'
errorlog = 'serve.err'
pidfile = 'serve.pid'
