"""
Gunicorn configuration for QuietPage production deployment.
Optimized for Django behind Nginx with moderate traffic.
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes: (2 x CPU cores) + 1, overridable via WEB_CONCURRENCY
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
graceful_timeout = 30
keepalive = 2

# Request limits (DoS protection)
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Application loading
# Preload app to reduce worker startup time and memory usage (copy-on-write)
preload_app = True
reload = os.environ.get("DEBUG", "False").lower() == "true"

# Logging
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
capture_output = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "quietpage"

# Server mechanics
daemon = False
pidfile = os.environ.get("GUNICORN_PID_FILE", None)
tmp_upload_dir = None


# Server hooks
def on_starting(server):
    server.log.info("Starting Gunicorn with %s workers", workers)


def when_ready(server):
    server.log.info("Gunicorn is ready. Spawning workers")


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
