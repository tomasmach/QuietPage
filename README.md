# 📖 QuietPage

**QuietPage** is a minimalist web application designed to provide a calm and reflective space for journaling and tracking mental wellbeing. It helps users develop habits for personal growth, mindfulness, and emotional awareness.

---

## 🌟 Features (Planned)

- **🖫 Daily Journaling**: Write and save personal entries with a simple editor.
- **😊 Mood Tracking**: Record daily mood ratings and see trends over time.
- **📊 Basic Analytics**: View statistics on writing habits and mood trends.
- **🔒 User Accounts**: Secure registration and login with private data storage.
- **🌙 Minimalist Design**: A distraction-free interface for focused writing.

---

## 🛠️ Technologies

- **Backend**: Django 5.2
- **Frontend**: HTML, CSS (Custom design system)
- **Database**: SQLite (Development) with future scalability to PostgreSQL
- **Python**: 3.14
- **Hosting**: Railway, Heroku, or Docker
- **Authentication**: Django built-in auth

---

## 🚀 Roadmap

### **MVP Release (Q1 2025)**
- Implement basic journaling features (create, read, update, delete entries).
- Add mood tracking and basic analytics.
- Set up user registration, login, and data security.
- Launch a functional and responsive user interface.

### **Future Plans**
- Advanced journaling tools (custom prompts, templates).
- Detailed analytics (mood trends, writing heatmaps).
- Mindfulness features (guided breathing, focus timers).
- Community challenges and social features.

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
# Spuštění testů
pytest

# Spuštění testů s pokrytím
pytest --cov=apps --cov-report=html

# Kontrola kódu
python manage.py check

# Django shell
python manage.py shell
```

---

## 💡 Project Goals

1. Provide a calm and intuitive platform for journaling and self-reflection.
2. Help users track their emotions and build mindful habits.
3. Continuously evolve based on user feedback.

---

Contributions, feedback, and ideas are welcome! Stay tuned for updates and the official release. 🌟
