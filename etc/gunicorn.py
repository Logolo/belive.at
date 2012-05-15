max_requests = 20000
timeout = 40
loglevel = 'warn'
workers = 3
worker_class = 'pyramid_socketio.gunicorn.workers.GeventSocketIOWorker'
