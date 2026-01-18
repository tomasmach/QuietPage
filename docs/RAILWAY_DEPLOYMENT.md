# Railway Deployment Guide

This guide explains how to deploy QuietPage to Railway.app.

## Prerequisites

- Railway account ([Railway](https://railway.app))
- GitHub repository connected to Railway
- Railway CLI (optional, for local testing)

## Deployment Steps

### 1. Create New Railway Project

1. Log in to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your QuietPage repository
5. Railway will auto-detect the Dockerfile and deploy

### 2. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable

### 3. Configure Environment Variables

In Railway project settings → Variables, add:

**Required variables:**

```bash
# Django settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key-here
FERNET_KEY_PRIMARY=your-fernet-key-here

# Domain configuration (use your Railway domain)
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app

# Security (Railway handles SSL termination)
SECURE_SSL_REDIRECT=True
```

**Generate secret keys:**

```bash
# Generate Django SECRET_KEY
python config/utils.py

# Generate FERNET_KEY_PRIMARY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Optional variables:**

```bash
# Worker concurrency (Railway auto-configures based on memory)
WEB_CONCURRENCY=4

# Email configuration (if using email features)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@quietpage.com
```

### 4. Deploy

Railway automatically deploys on every git push to your main branch.

**Manual deployment:**
1. Push changes to GitHub
2. Railway detects changes and rebuilds
3. Health check at `/api/health/` must pass before traffic is routed

**Check deployment status:**
- Railway dashboard shows build logs and deployment status
- Check application logs for errors

### 5. Post-Deployment

**Verify deployment:**
```bash
curl https://your-app.up.railway.app/api/health/
# Should return: {"status": "healthy"}
```

**Create superuser (via Railway CLI):**
```bash
railway run python manage.py createsuperuser
```

**Or connect to Django shell:**
```bash
railway run python manage.py shell
```

## How It Works

### Build Process

Railway uses the multi-stage Dockerfile:
1. **Stage 1**: Build frontend (Node.js)
   - Installs npm dependencies
   - Runs `npm run build` to create production bundle

2. **Stage 2**: Install Python dependencies
   - Installs requirements from `requirements/production.txt`

3. **Stage 3**: Combine everything
   - Copies frontend build artifacts
   - Copies Python dependencies
   - Sets up non-root user for security

### Deployment Process

Railway executes the `release` command from Procfile before starting the web service:
```bash
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
```

This ensures:
- Database migrations are applied
- Static files are collected
- Frontend assets are ready to serve

Then starts the web service:
```bash
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-4} --timeout 30 --access-logfile - --error-logfile -
```

### Health Checks

Railway uses the health check configuration from `railway.toml`:
```toml
[deploy]
healthcheckPath = "/api/health/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

The `/api/health/` endpoint is defined in `apps/api/urls.py` and returns:
```json
{"status": "healthy"}
```

## Configuration Files

### railway.toml
Defines build and deployment settings:
- Uses Dockerfile for build
- Health check endpoint
- Restart policy

### Procfile
Defines process types:
- `web`: Gunicorn server
- `release`: Pre-deployment commands (migrate, collectstatic)

### Dockerfile
Multi-stage build:
- Frontend build (Node.js)
- Python dependencies
- Final production image

### requirements/production.txt
Production Python dependencies including:
- `dj-database-url==2.3.0` - Parse Railway's DATABASE_URL
- `gunicorn==23.0.0` - Production WSGI server
- `psycopg2-binary` - PostgreSQL adapter

### config/settings/production.py
Production Django settings:
- DATABASE_URL support via `dj-database-url`
- Security headers (HSTS, CSP, X-Frame-Options)
- Static file configuration
- CORS and CSRF protection

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes (auto) | - |
| `PORT` | Web service port | Yes (auto) | 8000 |
| `DJANGO_SETTINGS_MODULE` | Django settings module | Yes | - |
| `SECRET_KEY` | Django secret key | Yes | - |
| `FERNET_KEY_PRIMARY` | Encryption key for journal entries | Yes | - |
| `ALLOWED_HOSTS` | Allowed domain names | Yes | - |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins | Yes | - |
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | No | True |
| `WEB_CONCURRENCY` | Gunicorn worker processes | No | 4 |
| `EMAIL_HOST` | SMTP server | No | - |
| `EMAIL_PORT` | SMTP port | No | 587 |
| `EMAIL_USE_TLS` | Use TLS for email | No | True |
| `EMAIL_HOST_USER` | SMTP username | No | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | No | - |

## Troubleshooting

### Build Fails

**Check build logs in Railway dashboard:**
- Frontend build errors: Check `frontend/package.json` scripts
- Python dependency errors: Check `requirements/production.txt`
- Docker build errors: Check `Dockerfile` syntax

### Deployment Fails

**Health check fails:**
```bash
# Check application logs
railway logs

# Verify DATABASE_URL is set
railway variables

# Test migrations manually
railway run python manage.py migrate --noinput
```

**Static files not found:**
```bash
# Run collectstatic manually
railway run python manage.py collectstatic --noinput --clear

# Check STATIC_ROOT setting in production.py
```

### Runtime Errors

**500 Internal Server Error:**
- Check Railway logs for Python tracebacks
- Verify all required environment variables are set
- Check database connection

**CSRF verification failed:**
- Verify CSRF_TRUSTED_ORIGINS matches your Railway domain
- Ensure ALLOWED_HOSTS includes your Railway domain
- Check that cookies are being sent with API requests

**Database connection errors:**
- Verify PostgreSQL service is running in Railway
- Check DATABASE_URL environment variable
- Test connection: `railway run python manage.py dbshell`

## Scaling

Railway automatically scales based on your plan:
- **Starter Plan**: 512MB RAM, 1 vCPU
- **Developer Plan**: 8GB RAM, 8 vCPU
- **Team Plan**: Custom resources

**Adjust worker processes:**
```bash
# Set in Railway environment variables
WEB_CONCURRENCY=8  # For larger instances
```

**Recommended worker formula:**
```text
workers = (2 x CPU cores) + 1
```

## Monitoring

**Check logs:**
```bash
# Real-time logs
railway logs --follow

# Filter by service
railway logs --service web
```

**Check metrics:**
- Railway dashboard shows CPU, memory, and network usage
- Set up alerts for resource usage

## Security Considerations

1. **Environment Variables**: Never commit secrets to git
2. **HTTPS Only**: Railway provides SSL termination automatically
3. **HSTS Headers**: Enabled by default in production settings
4. **CSP Headers**: Content Security Policy configured
5. **Database Backups**: Railway provides automatic backups
6. **Secret Rotation**: Rotate SECRET_KEY and FERNET_KEY_PRIMARY periodically

## Next Steps

- Set up custom domain (Railway supports custom domains)
- Configure email provider for password resets
- Set up monitoring and alerting
- Configure database backups
- Review security checklist in `docs/SECURITY_CHECKLIST.md`

## References

- Railway Documentation: https://docs.railway.app
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Gunicorn Configuration: https://docs.gunicorn.org/en/stable/settings.html
