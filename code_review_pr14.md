# Code Review: PR #14 - Feat/production deployment

**Review Date:** 2026-01-11
**Commit SHA:** c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd
**Issues Found:** 7 high-confidence issues

---

## Issues

### 1. Missing django-redis dependency breaks development environments (Score: 100)

**Description:** The cache backend was changed from `DatabaseCache` to `RedisCache` in `config/settings/base.py`, but the `django-redis` package is only added to `requirements/production.txt`, not `requirements/base.txt`. Development environments will fail to start because Django will try to import `django_redis.cache.RedisCache` which isn't installed.

**CLAUDE.md violation:** This breaks the development workflow. According to CLAUDE.md, developers should be able to run `make setup` and `make run`, but this now requires Redis and django-redis to be installed.

**Files affected:**
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/config/settings/base.py#L157-L169
- `requirements/base.txt` (missing django-redis)
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/requirements/production.txt#L8

**Fix:** Add `django-redis==6.0.0` to `requirements/base.txt`

---

### 2. Missing tests for new Celery task functionality (Score: 95)

**Description:** No tests were added for 625+ lines of new Celery task functionality. The new task modules in `apps/accounts/tasks.py` (210 lines), `apps/core/tasks.py` (182 lines), and `apps/journal/tasks.py` (233 lines) have 0% test coverage. Complex business logic including email verification, reminders, backups, and data exports should have comprehensive test coverage.

**CLAUDE.md violation:** "Backend: pytest with 80% coverage threshold" - Current total coverage is only 15.77%

**Files affected:**
- `apps/accounts/tasks.py` (210 lines, 0% coverage)
- `apps/core/tasks.py` (182 lines, 0% coverage)
- `apps/journal/tasks.py` (233 lines, 0% coverage)
- `apps/api/views.py` (HealthCheckView - no tests)

**Fix:** Add comprehensive test coverage for all new task modules

---

### 3. Makefile still references obsolete createcachetable command (Score: 95)

**Description:** The Makefile's `setup` target (line 42) and `cache` target (line 58) still run `python manage.py createcachetable`, which is incompatible with the Redis cache backend. This command only works with database-backed cache and will fail or create an unused table.

**Files affected:**
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/Makefile#L40-L43
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/Makefile#L55-L58

**Fix:** Remove `createcachetable` commands from Makefile since Redis doesn't use database tables for caching

---

### 4. Information disclosure in health check endpoint (Score: 85)

**Description:** The health check endpoint at `/api/health/` exposes detailed error messages including exception details via `str(e)` when components fail health checks. This is a security issue as it can leak sensitive information about system architecture, database structure, file paths, or internal configurations to unauthenticated users.

**CLAUDE.md violation:** "Always use best coding practices with a security-first approach"

**Files affected:**
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/apps/api/views.py#L463-L467 (database health check)
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/apps/api/views.py#L475-L479 (Redis health check)
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/apps/api/views.py#L490-L494 (Celery health check)

**Fix:** Return generic error messages to external callers and only log detailed exceptions internally

---

### 5. DEBUG=True hardcoded in production docker-compose.yml (Score: 85)

**Description:** The `docker-compose.yml` file explicitly sets `DEBUG=True` in environment variables for web, celery_worker, and celery_beat services, all while using `config.settings.production`. Running with DEBUG enabled in production exposes sensitive information through error pages and increases security vulnerabilities.

**CLAUDE.md violation:** "Always use best coding practices with a security-first approach"

**Files affected:**
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/docker-compose.yml#L44-L47 (web service)
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/docker-compose.yml#L88-L91 (celery_worker)
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/docker-compose.yml#L125-L128 (celery_beat)

**Fix:** Remove hardcoded `DEBUG=True` and rely on environment variables without defaults, or set `DEBUG=False` for production compose file

---

### 6. Hardcoded SSL certificate placeholder in Nginx config (Score: 85)

**Description:** The nginx configuration has hardcoded certificate paths pointing to `your-domain.com` which is obviously a placeholder. Nginx will fail to start if this config is deployed without modification.

**Files affected:**
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/nginx/conf.d/quietpage.conf#L28-L31

**Fix:** Use environment variable substitution or include clear deployment documentation. Consider validating certificate paths in docker-compose health checks before starting nginx.

---

### 7. Development settings don't override cache backend for local development (Score: 85)

**Description:** The `config/settings/development.py` file doesn't override the cache configuration, meaning development environments inherit the Redis cache from base.py. Developers following the README will use SQLite + Django dev server but unexpectedly need Redis for caching. This breaks the simple "clone and run" development workflow.

**Files affected:**
- `config/settings/development.py` (missing cache backend override)
- https://github.com/tomasmach/QuietPage/blob/c694a3e2be2edbd0333a5d0c1a8b64f8a88dc8bd/config/settings/base.py#L157-L169

**Fix:** Override `CACHES` in `development.py` to use either database cache or locmem cache for local development without Redis

---

## Additional Issues (Score 75-79)

These issues didn't meet the 80+ threshold but are worth noting:

- **Missing Celery timeout in health check** (75): Health check's Celery inspect() call can hang indefinitely
- **Hardcoded database credentials** (75): docker-compose.yml uses quietpage/quietpage as defaults
- **Health check marks app unhealthy if Redis fails** (75): Returns HTTP 503 even though app could function with degraded caching
- **Hardcoded Czech strings without i18n** (75): Email templates and forms lack Django translation framework usage

---

## Summary

**Critical Issues (100):** 1
**High Priority (95):** 2
**Important (85):** 4

The most critical issues that should block merging:
1. Missing django-redis dependency (breaks development)
2. Missing test coverage (violates project standards)
3. Obsolete Makefile commands (breaks setup workflow)

**Recommendation:** Address at minimum issues #1, #2, and #3 before merging. Issues #4 and #5 are security concerns that should also be resolved.
