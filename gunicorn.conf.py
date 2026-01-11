"""
Gunicorn configuration file for QuietPage production deployment.

This configuration optimizes performance, reliability, and security for a Django application
running behind Nginx with moderate traffic expectations.
"""

import multiprocessing
import os

# =============================================================================
# Server Socket
# =============================================================================

# The socket to bind. Use 0.0.0.0 to make the server available externally
bind = "0.0.0.0:8000"

# Allow pending connections to queue up to this number
backlog = 2048


# =============================================================================
# Worker Processes
# =============================================================================

# Number of worker processes for handling requests
# Formula: (2 x CPU cores) + 1
# This can be overridden by the WEB_CONCURRENCY environment variable
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))

# The type of workers to use
# Options: sync, gevent, eventlet, tornado, gthread
# For Django, 'sync' is recommended for CPU-bound apps, 'gthread' for I/O-bound apps
worker_class = "sync"

# Number of threads per worker (only for gthread worker_class)
# threads = 2

# Maximum number of requests a worker will process before restarting
# This helps prevent memory leaks from accumulating
max_requests = 1000

# Randomize max_requests to avoid all workers restarting at the same time
max_requests_jitter = 50


# =============================================================================
# Timeouts
# =============================================================================

# Workers silent for more than this many seconds are killed and restarted
timeout = 30

# Timeout for graceful workers restart
# Workers receiving a SIGTERM signal will have this long to finish serving requests
graceful_timeout = 30

# The number of seconds to wait for requests on a Keep-Alive connection
keepalive = 2


# =============================================================================
# Security & Performance
# =============================================================================

# Limit the allowed size of an HTTP request line
# This helps prevent DoS attacks
limit_request_line = 4094

# Limit the number of HTTP headers in a request
limit_request_fields = 100

# Limit the allowed size of an HTTP request header field
limit_request_field_size = 8190


# =============================================================================
# Application Loading
# =============================================================================

# Load application code before the worker processes are forked
# This saves memory by sharing code across workers
# WARNING: This can cause issues with database connections and file handles
#          Only enable if your application handles forking properly
preload_app = False

# Restart workers when code changes (development only)
reload = os.environ.get("DEBUG", "False").lower() == "true"


# =============================================================================
# Logging
# =============================================================================

# The Access log file to write to
# Use '-' to log to stdout
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")

# The Error log file to write to
# Use '-' to log to stderr
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")

# The granularity of Error log outputs
# Options: debug, info, warning, error, critical
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Redirect stdout/stderr to the error log
capture_output = True

# Access log format
# h = remote address, l = '-', u = user name, t = date/time, r = request line
# s = status, b = response length, f = referer, a = user agent, D = request time in microseconds
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'


# =============================================================================
# Process Naming
# =============================================================================

# A base to use with setproctitle to change the way that Gunicorn processes are reported in the system process table
proc_name = "quietpage"


# =============================================================================
# Server Mechanics
# =============================================================================

# Daemonize the Gunicorn process
# Detaches the server from the controlling terminal and enters the background
daemon = False

# A filename to use for the PID file
# If not set, no PID file will be written
pidfile = os.environ.get("GUNICORN_PID_FILE", None)

# A directory to store temporary request data
# This should be a location on a fast filesystem
tmp_upload_dir = None


# =============================================================================
# Server Hooks
# =============================================================================

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn with %s workers", workers)


def on_reload(server):
    """Called when a worker is reloaded (only when reload=True)."""
    server.log.info("Reloading Gunicorn")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn is ready. Spawning workers")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received SIGINT or SIGQUIT")


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT")
