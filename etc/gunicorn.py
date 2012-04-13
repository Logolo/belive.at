import logging
import os
import signal
import sys

def on_starting(server):
    # use server hook to patch socket to allow worker reloading
    from gevent import monkey
    monkey.patch_socket()

def post_fork(server, worker):
    from psycogreen.gevent import psyco_gevent
    psyco_gevent.make_psycopg_green()
    worker.log.info("Patched psycopg2 to work with gevent.")

def when_ready(server):
    def monitor():
        modify_times = {}
        while True:
            for module in sys.modules.values():
                path = getattr(module, "__file__", None)
                if not path: continue
                if path.endswith(".pyc") or path.endswith(".pyo"):
                    path = path[:-1]
                try:
                    modified = os.stat(path).st_mtime
                except:
                    continue
                if path not in modify_times:
                    modify_times[path] = modified
                    continue
                if modify_times[path] != modified:
                    logging.info("%s modified; restarting server", path)
                    os.kill(os.getpid(), signal.SIGHUP)
                    modify_times = {}
                    break
            gevent.sleep(1)
    import gevent
    gevent.spawn(monitor)

max_requests = 20000
#preload_app = True
timeout = 40
loglevel = 'info'
worker_class = 'pyramid_socketio.gunicorn.workers.GeventSocketIOWorker'
