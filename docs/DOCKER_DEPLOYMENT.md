# Docker Deployment Guide - QuietPage

Tato příručka popisuje jak nasadit QuietPage pomocí Dockeru.

## Přehled

QuietPage používá multi-stage Docker build a docker-compose pro orchestraci služeb:
- **db**: PostgreSQL 16 database
- **redis**: Redis cache a Celery broker
- **web**: Django aplikace s Gunicorn
- **celery_worker**: Celery worker pro background tasks
- **celery_beat**: Celery beat scheduler pro periodic tasks
- **nginx** (prod): Reverse proxy a static file serving
- **certbot** (prod): SSL certifikáty (Let's Encrypt)

---

## Development Setup

### 1. Připrav .env soubor

```bash
cp .env.example .env
```

Uprav hodnoty v `.env`:
```bash
SECRET_KEY=your-secret-key-here
FERNET_KEY_PRIMARY=your-fernet-key-here
DB_NAME=quietpage
DB_USER=quietpage
DB_PASSWORD=quietpage
```

### 2. Build a spuštění

```bash
# Build Docker image
docker-compose build

# Spusť všechny služby
docker-compose up

# Nebo v pozadí
docker-compose up -d
```

### 3. Inicializace databáze

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create cache table (pokud používáš database cache)
docker-compose exec web python manage.py createcachetable

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Přístup k aplikaci

- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

### 5. Monitorování

```bash
# Sleduj logy všech služeb
docker-compose logs -f

# Sleduj logy konkrétní služby
docker-compose logs -f web
docker-compose logs -f celery_worker

# Zkontroluj status služeb
docker-compose ps

# Zkontroluj health check
curl http://localhost:8000/api/health/
```

### 6. Zastavení

```bash
# Zastav všechny služby
docker-compose down

# Zastav a smaž volumes (data budou ztracena!)
docker-compose down -v
```

---

## Production Setup

### 1. Připrav production .env soubor

```bash
# Vygeneruj nové production keys (NIKDY nepoužívej dev klíče!)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
FERNET_KEY_PRIMARY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

Uprav `.env` pro production:
```bash
# Django
SECRET_KEY=<new-production-secret-key>
FERNET_KEY_PRIMARY=<new-production-fernet-key>
DJANGO_SETTINGS_MODULE=config.settings.production

# Database
DB_NAME=quietpage_prod
DB_USER=quietpage_prod
DB_PASSWORD=<strong-password>

# Allowed hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@quietpage.com

# Site URL
SITE_URL=https://yourdomain.com

# Sentry (optional)
SENTRY_DSN=https://...@sentry.io/...
```

### 2. Aktualizuj nginx konfiguraci

Uprav `nginx/conf.d/quietpage.conf`:
- Změň `server_name _` na `server_name yourdomain.com www.yourdomain.com`
- Uprav SSL certificate cesty

### 3. Získání SSL certifikátu

```bash
# První spuštění - získání certifikátu
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

### 4. Build a spuštění production

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Spusť všechny služby
docker-compose -f docker-compose.prod.yml up -d

# Inicializuj databázi
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 5. Verifikace

```bash
# Zkontroluj Django security checks
docker-compose -f docker-compose.prod.yml exec web python manage.py check --deploy

# Zkontroluj health endpoint
curl https://yourdomain.com/api/health/

# Zkontroluj SSL
curl -I https://yourdomain.com
```

### 6. Monitoring

```bash
# Sleduj production logy
docker-compose -f docker-compose.prod.yml logs -f

# Zkontroluj status
docker-compose -f docker-compose.prod.yml ps

# Zkontroluj Celery worker
docker-compose -f docker-compose.prod.yml exec celery_worker celery -A config inspect active
```

---

## Maintenance

### Backup Database

```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U quietpage_prod quietpage_prod > backup_$(date +%Y%m%d).sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U quietpage_prod quietpage_prod
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build web celery_worker celery_beat
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f web

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 web
```

### Shell Access

```bash
# Django shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec db psql -U quietpage quietpage

# Redis CLI
docker-compose exec redis redis-cli

# Container bash
docker-compose exec web bash
```

---

## Troubleshooting

### Web service won't start

```bash
# Zkontroluj logy
docker-compose logs web

# Zkontroluj environment variables
docker-compose exec web env

# Zkontroluj databázi
docker-compose exec db pg_isready -U quietpage
```

### Database connection errors

```bash
# Zkontroluj že DB je healthy
docker-compose ps

# Restart DB
docker-compose restart db

# Zkontroluj DB logy
docker-compose logs db
```

### Static files not loading

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Zkontroluj nginx konfiguraci
docker-compose exec nginx nginx -t

# Reload nginx
docker-compose exec nginx nginx -s reload
```

### Celery tasks not running

```bash
# Zkontroluj Celery worker status
docker-compose exec celery_worker celery -A config inspect active

# Restart worker
docker-compose restart celery_worker

# Zkontroluj Redis
docker-compose exec redis redis-cli ping
```

### SSL certificate renewal failing

```bash
# Test renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal

# Zkontroluj nginx config
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

---

## Security Checklist

Před production deploymentem zkontroluj:

- [ ] Nové SECRET_KEY a FERNET_KEY_PRIMARY vygenerované
- [ ] DEBUG=False v production settings
- [ ] ALLOWED_HOSTS správně nastavené
- [ ] SSL certifikáty instalované a validní
- [ ] Firewall nastavený (pouze porty 80, 443)
- [ ] Database backups nakonfigurované
- [ ] Monitoring (Sentry) aktivní
- [ ] Rate limiting funguje (zkontroluj nginx config)
- [ ] Security headers přítomné (curl -I https://yourdomain.com)

---

## Užitečné příkazy

```bash
# Rebuild bez cache
docker-compose build --no-cache

# Remove all stopped containers
docker-compose down

# Remove volumes
docker-compose down -v

# View resource usage
docker stats

# Clean up Docker system
docker system prune -a
```

---

**Pro další informace viz:**
- [SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md) - Pre-production security checklist
- [README.md](README.md) - General project documentation
