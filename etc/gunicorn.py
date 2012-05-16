max_requests = 20000
loglevel = 'warn'
pidfile = 'serve.pid'
timeout = 40
workers = 3
worker_class = 'pyramid_socketio.gunicorn.workers.GeventSocketIOWorker'
