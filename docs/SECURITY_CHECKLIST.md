# QuietPage - Pre-Production Security Checklist

**Před nasazením do produkce MUSÍŠ projít celý tento checklist!**

---

## 1. Environment Variables

### 1.1 Verify No Secrets in Git

```bash
# Check git history for .env file
git log --all --full-history --source --patch -- .env

# Search for any committed encryption keys
git log --all --source --patch -S "FERNET_KEY_PRIMARY"

# Search for any committed secret keys
git log --all --source --patch -S "SECRET_KEY"
```

**✅ Akce:** Pokud najdeš .env nebo klíče v historii, jsou **COMPROMISED** a musíš:
1. Vygenerovat NOVÉ klíče
2. Re-encryptovat všechna data s novým FERNET_KEY
3. Vyčistit git historii: `git filter-repo --path .env --invert-paths`

### 1.2 Verify .gitignore

```bash
# Check .env is in .gitignore
grep "^\.env$" .gitignore
```

**✅ Očekávaný výstup:** `.env` (pokud není, přidej ho!)

### 1.3 Required Environment Variables

**Production server MUSÍ mít tyto env variables:**

```bash
# CRITICAL - Security Keys
export SECRET_KEY="<50+ random characters>"
export FERNET_KEY_PRIMARY="<44-byte base64 key>"

# Hosting
export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# Database
export DB_ENGINE=django.db.backends.postgresql
export DB_NAME=quietpage_prod
export DB_USER=quietpage
export DB_PASSWORD=<strong-password>
export DB_HOST=localhost
export DB_PORT=5432

# Email
export EMAIL_HOST=smtp.example.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=noreply@yourdomain.com
export EMAIL_HOST_PASSWORD=<email-password>
export DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Django Settings
export DJANGO_SETTINGS_MODULE=config.settings.production
```

---

## 2. Generate Secure Keys

### 2.1 Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**✅ Požadavky:**
- Minimálně 50 znaků
- Náhodný, kryptograficky bezpečný
- NIKDY nepoužívej default: `django-insecure-please-change-this-in-env-file`

### 2.2 Generate FERNET_KEY_PRIMARY

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**✅ Požadavky:**
- Přesně 44 bytů (base64-encoded 32-byte key)
- Náhodný, kryptograficky bezpečný
- Uložený v .env, NIKDY v kódu

### 2.3 Test Key Validation

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py check
```

**✅ Očekávaný výstup:** `System check identified no issues`

**❌ Pokud vidíš `ImproperlyConfigured`:** Oprav env variables podle chybové zprávy.

---

## 3. Database Security

### 3.1 PostgreSQL User Permissions

```sql
-- Create dedicated user (NOT superuser)
CREATE USER quietpage WITH PASSWORD 'strong-password';

-- Grant minimal permissions
GRANT CONNECT ON DATABASE quietpage_prod TO quietpage;
GRANT USAGE ON SCHEMA public TO quietpage;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO quietpage;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO quietpage;

-- Revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM quietpage;
```

### 3.2 Database Connection Security

**✅ Checklist:**
- [ ] Database uses SSL/TLS encryption
- [ ] Database password je strong (20+ random chars)
- [ ] Database je accessible pouze z app serveru (firewall rules)
- [ ] Database má regular automated backups

---

## 4. Django Security Settings Verification

### 4.1 Run Django Security Check

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py check --deploy
```

**✅ Očekávaný výstup:** Žádné CRITICAL nebo ERROR warnings.

### 4.2 Manual Settings Verification

Zkontroluj `config/settings/production.py`:

```python
# Must be False
DEBUG = False  # ✅

# Must be set
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']  # ✅

# HTTPS settings
SECURE_SSL_REDIRECT = True  # ✅
SESSION_COOKIE_SECURE = True  # ✅
CSRF_COOKIE_SECURE = True  # ✅
SESSION_COOKIE_HTTPONLY = True  # ✅
SESSION_COOKIE_SAMESITE = 'Lax'  # ✅
CSRF_COOKIE_SAMESITE = 'Lax'  # ✅

# HSTS
SECURE_HSTS_SECONDS = 31536000  # ✅
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # ✅
SECURE_HSTS_PRELOAD = True  # ✅

# Security headers
SECURE_BROWSER_XSS_FILTER = True  # ✅
SECURE_CONTENT_TYPE_NOSNIFF = True  # ✅
X_FRAME_OPTIONS = 'DENY'  # ✅
```

---

## 5. Encryption Key Rotation (Pokud je klíč compromised)

### 5.1 Check if Key Needs Rotation

**Rotate FERNET_KEY_PRIMARY pokud:**
- ❌ Byl commitnutý do git (i když jen v historii)
- ❌ Byl leaked do logů
- ❌ Máš podezření na kompromis
- ❌ Používáš default/test key

### 5.2 Rotation Process (COMPLEX - Dělej opatrně!)

**⚠️ VAROVÁNÍ:** Tohle je destruktivní operace. Musíš mít backup!

```bash
# 1. Backup database
pg_dump quietpage_prod > backup_before_rotation.sql

# 2. Generate NEW key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Run rotation command (from plan - Phase 4.1)
# NOTE: Tento command ještě neexistuje, implementuj podle plánu!
# python manage.py rotate_encryption_key --new-key=<NEW_KEY>

# 4. Update .env with new key
# 5. Restart application
# 6. Verify entries are readable
```

---

## 6. Static Files & Media

### 6.1 Collect Static Files

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput
```

### 6.2 Media Files Security

**✅ Checklist:**
- [ ] Media files (`media/avatars/`) NEJSOU v git repository
- [ ] Media files mají správná oprávnění (readable by web server)
- [ ] Media uploads jsou size-limited (max 5MB per avatar)
- [ ] Media folder má regular backups

---

## 7. Email Configuration Test

### 7.1 Test Email Sending

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'QuietPage Test Email',
    'Pokud vidíš tento email, konfigurace je OK!',
    'noreply@yourdomain.com',
    ['your@email.com'],
    fail_silently=False,
)
```

**✅ Očekávaný výstup:** Email delivered bez errors.

---

## 8. Rate Limiting & Brute Force Protection

### 8.1 Verify django-axes is Installed

```bash
pip list | grep django-axes
```

**✅ Očekávaný výstup:** `django-axes==6.5.1` (nebo novější)

### 8.2 Test Rate Limiting

1. Otevři `/accounts/login/` v browseru
2. Zadej špatné heslo 5x po sobě
3. 6. pokus by měl vrátit **403 Forbidden**

**✅ Očekávaný výsledek:** Locked out po 5 failed attempts.

---

## 9. SSL/TLS Certificate

### 9.1 Verify SSL Certificate

```bash
# Test SSL certificate validity
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com < /dev/null
```

**✅ Checklist:**
- [ ] Certificate je platný (not expired)
- [ ] Certificate je pro správnou doménu
- [ ] Certificate chain je complete
- [ ] Using TLS 1.2+ (ne SSL 3.0 nebo TLS 1.0)

### 9.2 Test HSTS Headers

```bash
curl -I https://yourdomain.com | grep -i strict
```

**✅ Očekávaný výstup:** `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

---

## 10. Migrations & Database

### 10.1 Run Migrations

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
```

**✅ Očekávaný výstup:** All migrations applied successfully.

### 10.2 Create Superuser

```bash
python manage.py createsuperuser
```

**⚠️ DŮLEŽITÉ:**
- Použij strong password (20+ chars, mixed case, numbers, symbols)
- NIKDY nepoužívej default `admin/admin123` z dev environment!
- Ulož credentials do password manageru

---

## 11. File Permissions

### 11.1 Application Files

```bash
# Application code should be read-only for web server user
chown -R yourusername:www-data /path/to/QuietPage
chmod -R 755 /path/to/QuietPage

# Sensitive files
chmod 600 .env
chmod 600 config/settings/production.py
```

### 11.2 Media & Static Files

```bash
# Media files writable by web server
chown -R www-data:www-data /path/to/QuietPage/media
chmod -R 755 /path/to/QuietPage/media

# Static files readable by web server
chmod -R 755 /path/to/QuietPage/staticfiles
```

---

## 12. Logging & Monitoring

### 12.1 Verify Logging Configuration

```bash
# Check logs directory exists
ls -la /path/to/QuietPage/logs/

# Test log rotation works
python manage.py check
tail -f /path/to/QuietPage/logs/django.log
```

### 12.2 Monitor for Errors

**✅ Checklist:**
- [ ] Logs jsou writable by Django
- [ ] Log rotation je configured (max 10MB per file)
- [ ] Security events jsou logged (viz `apps/accounts/security_logger.py`)
- [ ] Logs NEOBSAHUJÍ sensitive data (passwords, encryption keys)

---

## 13. Backup Strategy

### 13.1 Database Backups

```bash
# Automated daily backups
0 2 * * * pg_dump quietpage_prod > /backups/quietpage_$(date +\%Y\%m\%d).sql
```

**✅ Checklist:**
- [ ] Daily automated backups
- [ ] Backups jsou stored off-server
- [ ] Backups jsou encrypted
- [ ] Tested restore procedure (alespoň jednou!)

### 13.2 Media Backups

```bash
# Backup avatars weekly
0 3 * * 0 tar -czf /backups/media_$(date +\%Y\%m\%d).tar.gz /path/to/QuietPage/media/
```

---

## 14. Final Pre-Launch Checklist

**Projdi tenhle checklist těsně před launchemm:**

- [ ] ✅ Všechny env variables jsou set v production
- [ ] ✅ Git history NEOBSAHUJE secrets
- [ ] ✅ SECRET_KEY je strong a unique
- [ ] ✅ FERNET_KEY_PRIMARY je strong a unique
- [ ] ✅ ALLOWED_HOSTS je správně set
- [ ] ✅ DEBUG = False v production
- [ ] ✅ SSL certificate je platný
- [ ] ✅ HSTS headers jsou enabled
- [ ] ✅ Database backups jsou automated
- [ ] ✅ Email sending funguje
- [ ] ✅ Rate limiting je functional
- [ ] ✅ All migrations applied
- [ ] ✅ Superuser account created (strong password!)
- [ ] ✅ `python manage.py check --deploy` prošel bez errors
- [ ] ✅ Static files collected
- [ ] ✅ Media folder permissions jsou correct
- [ ] ✅ Logs jsou writable a rotated

---

## 15. Post-Launch Monitoring

**První 24 hodin po launch:**

1. **Monitor logs každou hodinu:**
   ```bash
   tail -f /path/to/QuietPage/logs/django.log
   tail -f /path/to/QuietPage/logs/security.log
   ```

2. **Check for errors:**
   ```bash
   grep ERROR /path/to/QuietPage/logs/django.log
   ```

3. **Monitor failed login attempts:**
   ```bash
   grep "axes" /path/to/QuietPage/logs/security.log
   ```

4. **Test critical paths:**
   - ✅ User registration works
   - ✅ Email verification works
   - ✅ Entry creation works
   - ✅ Entry encryption/decryption works
   - ✅ Password reset works

---

## Emergency Contacts

**Pokud něco selže:**

1. **Encryption key compromised:**
   - Immediately rotate FERNET_KEY_PRIMARY (viz sekce 5)
   - Notify all users to change passwords

2. **Database compromised:**
   - Restore from latest backup
   - Rotate ALL secrets
   - Force password reset for all users

3. **500 errors po deployment:**
   - Check logs: `tail -f logs/django.log`
   - Verify env variables: `python manage.py check --deploy`
   - Rollback to previous version if critical

---

## Compliance & Privacy

**GDPR Considerations:**

- [ ] User data deletion works (cascade deletes)
- [ ] Privacy policy je updated a dostupná
- [ ] Cookie consent je implemented (pokud používáš analytics)
- [ ] Users můžou exportovat svá data

---

**Poslední update:** 2024-01-XX
**Autor:** Tomas Mach
**Status:** Pre-launch security hardening complete ✅
