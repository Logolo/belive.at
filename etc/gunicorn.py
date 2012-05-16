max_requests = 20000
loglevel = 'warn'
timeout = 40
workers = 3
worker_class = 'pyramid_socketio.gunicorn.workers.GeventSocketIOWorker'

accesslog = 'serve.out'
errorlog = 'serve.err'
pidfile = 'serve.pid'
