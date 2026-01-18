# 📖 QuietPage

**QuietPage** is a privacy-focused journaling and mindfulness application with end-to-end encryption, intelligent streak tracking, and comprehensive analytics. Built with Django REST API and React SPA, featuring an "analog tech" aesthetic for distraction-free writing.

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/QuietPage.git
cd QuietPage

# Install dependencies (Python + Node.js)
make install-dev

# Setup database and create superuser
make setup

# Start development servers (Django + Vite)
make dev
```

Visit **http://localhost:5173** to access the application.

For detailed setup instructions, see [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).

---

## 🌟 Features (Planned)

- **📝 Daily Journaling**: Auto-creating daily entries with real-time auto-save (750words.com style)
- **🔒 End-to-End Encryption**: Server-side Fernet encryption (AES-128-CBC + HMAC-SHA256) for all entry content
- **😊 Mood Tracking**: Record daily mood ratings (1-5 scale) and visualize trends over time
- **📊 Comprehensive Analytics**: Heatmaps, mood charts, word count trends, writing patterns, and personal records
- **🔥 Streak Tracking**: Timezone-aware consecutive writing day tracking with goal achievements
- **🏷️ Tag System**: Flexible tagging with usage analytics and mood correlations
- **🌙 Dual Themes**: Midnight (dark) and Paper (light) with "analog tech" aesthetic
- **🌍 Internationalization**: Czech and English language support
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

---

## 🛠️ Technologies

### Backend
- **Django**: 5.2+ with Django REST Framework
- **Python**: 3.14 (managed with `uv` package manager)
- **Database**: PostgreSQL 16 (Production), SQLite (Development)
- **Cache & Queue**: Redis 7 + Celery for async tasks
- **Web Server**: Gunicorn (WSGI) behind Nginx (reverse proxy)
- **Encryption**: Fernet (AES-128-CBC + HMAC-SHA256)

### Frontend
- **React**: 19.2.0 with TypeScript 5.9.3
- **Build Tool**: Vite 7.2.4 with HMR
- **Styling**: Tailwind CSS 3.4.17 with custom design system
- **Routing**: React Router 7.11.0
- **Charts**: Recharts 3.6.0
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Hosting**: Railway (PaaS) or self-hosted Docker
- **SSL**: Let's Encrypt (Certbot)
- **CI/CD**: Zero-downtime deployment with automatic rollback

---

## 🚀 Project Status

### **Current Version: 1.0 (MVP Complete)**

✅ **Completed Features:**
- Full CRUD for journal entries with encryption
- Auto-save functionality (750words.com style)
- Mood tracking and comprehensive analytics
- Streak tracking with timezone awareness
- Tag system with analytics
- User authentication and profile management
- Dashboard with featured entries and statistics
- Responsive design with dual themes (Midnight & Paper)
- Docker deployment with Railway support

### **In Progress:**
- Enhanced data visualizations
- Advanced search and filtering
- Export functionality (PDF, EPUB, Markdown)

### **Future Plans**
- Mobile applications (React Native or PWA)
- Advanced journaling tools (custom prompts, templates)
- Mindfulness features (guided breathing, focus timers)
- Real-time collaboration features (opt-in)
- ML-based sentiment analysis and mood prediction

---

## 📦 Instalace a nastavení pro vývojáře

### Požadavky
- Python 3.14+
- pip
- virtualenv (doporučeno)
- Git

### Kroky instalace

1. **Naklonujte repozitář**
   ```bash
   git clone https://github.com/your-username/QuietPage.git
   cd QuietPage
   ```

2. **Vytvořte a aktivujte virtuální prostředí**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```

3. **Nainstalujte závislosti**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Nastavte proměnné prostředí**

   Vytvořte soubor `.env` v kořenovém adresáři projektu:
   ```bash
   # Django nastavení
   SECRET_KEY=your-secret-key-here
   DJANGO_SETTINGS_MODULE=config.settings.development

   # Šifrovací klíč pro deníkové záznamy
   FERNET_KEY_PRIMARY=your-fernet-key-here
   ```

   Pro vygenerování Fernet klíče použijte:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

5. **Dokončete setup databáze**

   **Možnost A: Automatický setup (doporučeno)**
   ```bash
   make setup
   ```
   Tento příkaz automaticky:
   - Aplikuje všechny migrace
   - Vytvoří cache tabulku
   - Vytvoří superuživatelský účet

   **Možnost B: Manuální setup (krok po kroku)**

   a) Aplikujte migrace databáze
   ```bash
   python manage.py migrate
   ```

   b) **Vytvořte cache tabulku** ⚠️ **DŮLEŽITÉ**

   Projekt používá databázovou cache, která vyžaduje vytvoření speciální tabulky:
   ```bash
   python manage.py createcachetable
   # nebo: make cache
   ```

   Tento krok je **povinný** - bez něj nebude cache fungovat správně a můžete narazit na chyby.

   c) Vytvořte superuživatele (admin účet)
   ```bash
   python manage.py createsuperuser
   # nebo: make superuser
   ```

6. **Spusťte vývojový server**
   ```bash
   python manage.py runserver
   # nebo: make run
   ```

7. **Otevřete aplikaci v prohlížeči**

   Přejděte na: http://127.0.0.1:8000/

### Další užitečné příkazy

```bash
# Backend commands
make run               # Start Django dev server only
make test              # Run backend tests
make shell             # Django interactive shell
make migrate           # Apply database migrations
make makemigrations    # Create new migrations

# Frontend commands
cd frontend
npm run dev            # Start Vite dev server only
npm run build          # Production build
npm run test           # Run frontend tests
npm run lint           # ESLint

# Full stack development
make dev-full          # Start Redis + Django + Vite + Celery
make celery-worker     # Start Celery worker only
make celery-beat       # Start Celery beat scheduler only

# Testing with coverage
uv run pytest --cov=apps --cov-report=html
```

> **Poznámka:** Pro podrobné informace o vývoji, testování a deployment viz dokumentaci v `docs/`:
> - [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) - Development workflow
> - [TESTING.md](docs/TESTING.md) - Testing guidelines
> - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

---

## 📚 Documentation

QuietPage includes comprehensive documentation for developers:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete system architecture overview
- **[API.md](docs/API.md)** - REST API endpoints documentation
- **[DATABASE.md](docs/DATABASE.md)** - Database schema and relationships
- **[LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)** - Development environment setup
- **[DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)** - Self-hosted Docker deployment
- **[RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md)** - Railway PaaS deployment
- **[SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md)** - Security best practices
- **[TESTING.md](docs/TESTING.md)** - Testing strategy and guidelines
- **[CLAUDE.md](CLAUDE.md)** - AI assistant integration guide
- **[styles.md](styles.md)** - Design system and UI guidelines

### Implementation Plans

The `docs/plans/` directory contains dated implementation plans for major features:
- Design documents (UX specifications)
- Implementation guides (step-by-step execution)

---

## 💡 Project Goals

1. Provide a calm and intuitive platform for journaling and self-reflection.
2. Help users track their emotions and build mindful habits.
3. Continuously evolve based on user feedback.

---

Contributions, feedback, and ideas are welcome! Stay tuned for updates and the official release. 🌟
