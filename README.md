# Personal Journal Application

A web-based personal journal application with a clean, modern design, built with Django, Tailwind CSS, and HTMX.

## Features

- User authentication (login/registration)
- Write and save journal entries with timestamps
- Calendar date picker to view entries by date
- Clean, modern UI design with Tailwind CSS
- Theme toggle (light/dark mode) with hamburger menu
- Hamburger menu navigation (username, theme toggle, logout)
- Mobile-responsive design (consistent hamburger menu across all screen sizes)
- Dynamic content updates with HTMX (no page reloads)
- SQLite database for local storage
- Django admin interface for data management
- Docker support for easy deployment

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Tailwind CSS 3.x (CDN) + HTMX
- **Database**: SQLite3
- **Testing**: pytest with pytest-django
- **Code Quality**: Ruff formatter and linter
- **Deployment**: Docker with docker-compose

## Quick Start for Home Server Deployment

**Prerequisites:** Docker and Docker Compose installed on your home server

Deploy the application in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/Nithin-Anand/reflections.git
cd reflections

# 2. Generate a secret key
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# 3. Create .env file with your configuration
cat > .env << EOF
DJANGO_SECRET_KEY=$SECRET_KEY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$(hostname -I | awk '{print $1}'),$(hostname)
DATA_DIR=/app/data
EOF

# 4. Secure the .env file
chmod 600 .env

# 5. Deploy with Docker Compose
docker-compose up -d

# 6. Create your admin user
docker-compose exec journal uv run python manage.py createsuperuser

# 7. Access the application
echo "Application running at: http://$(hostname -I | awk '{print $1}'):8000"
```

**That's it!** Your journal is now running.

**Next steps:**
- Navigate to the application in your browser
- Log in with your admin credentials
- Start journaling!
- (Optional) See "Environment Variables Setup" below for advanced configuration
- (Optional) See "Production Considerations" for HTTPS setup and backups

---

## Local Development Setup

For local development without Docker:

## Installation

1. Install dependencies using uv:
```bash
uv sync
```

## Running the Application

1. Apply database migrations:
```bash
uv run python manage.py migrate
```

2. Create a superuser (for admin access):
```bash
uv run python manage.py createsuperuser
```

3. Start the development server:
```bash
uv run python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Docker Deployment (Detailed Configuration)

For detailed Docker configuration options, manual deployment, or troubleshooting, see below.

### Manual Docker Compose Commands

1. Build and start the application:
```bash
docker-compose up -d
```

2. Create a superuser (first time only):
```bash
docker-compose exec journal python manage.py createsuperuser
```

3. View logs:
```bash
docker-compose logs -f journal
```

4. Stop the application:
```bash
docker-compose down
```

The application will be available at `http://localhost:8000`

**Data Persistence:**
- SQLite database is stored in a Docker volume named `journal_data`
- The database file is located at `/app/data/db.sqlite3` inside the container
- Data persists across container restarts and rebuilds

### Environment Variables Setup

#### Required Environment Variables for Production

For production deployment, you **must** configure these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | **Yes** | Insecure default | Cryptographic signing key - must be unique and secret |
| `DJANGO_DEBUG` | No | `False` | Debug mode - must be `False` in production |
| `DJANGO_ALLOWED_HOSTS` | **Yes** | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames/IPs |
| `DATA_DIR` | No | Auto-set in Docker | Directory for database storage |

#### Step-by-Step Setup

**1. Generate a secure secret key:**

```bash
# Generate using Python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Or using OpenSSL
openssl rand -base64 50
```

**2. Create a `.env` file in your project directory:**

```bash
# Create .env file (replace values with your own)
cat > .env << 'EOF'
DJANGO_SECRET_KEY=your-generated-secret-key-from-step-1
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-server-ip,yourdomain.com
DATA_DIR=/app/data
EOF
```

**3. Secure the `.env` file:**

```bash
# Make it readable only by you
chmod 600 .env

# Verify it's in .gitignore (already included)
grep "^\.env$" .gitignore
```

**4. Deploy with Docker Compose:**

```bash
# Docker Compose automatically loads .env from the same directory
docker-compose up -d
```

#### Example .env File

```env
# REQUIRED: Generate your own secret key (see step 1 above)
DJANGO_SECRET_KEY=django-insecure-example-change-this-to-a-real-secret-key

# REQUIRED: Set to False for production
DJANGO_DEBUG=False

# REQUIRED: Add your server's IP address or domain name
DJANGO_ALLOWED_HOSTS=192.168.1.100,homeserver.local,yourdomain.com

# Optional: Automatically set in Docker
DATA_DIR=/app/data
```

#### Security Best Practices

1. **Never commit `.env` to version control** - It's already in `.gitignore`
2. **Backup your secret key** - Store it in a password manager
3. **Use a unique key per environment** - Don't reuse between dev/prod
4. **Restrict file permissions** - `chmod 600 .env`
5. **Rotate keys if compromised** - Generate a new key and update `.env`

#### Important Notes

⚠️ **Changing the secret key will:**
- Invalidate all user sessions (users must log in again)
- Invalidate password reset tokens
- Invalidate signed cookies

✅ **The `.env` file is automatically loaded by Docker Compose** - No additional configuration needed

## Updating the Application

When a new version is released, update your deployment while preserving all data:

```bash
# Navigate to your application directory
cd reflections

# Pull latest changes from git
git pull origin main

# Rebuild and restart (data persists automatically)
docker-compose up -d --build

# Verify everything is working
docker-compose logs -f journal
```

**What happens during update:**
- ✅ New code is deployed
- ✅ Database migrations run automatically (via `entrypoint.sh`)
- ✅ All your journal entries are preserved in the volume
- ✅ User accounts and sessions remain intact

**Rollback if needed:**
```bash
# Go back to previous version
git log --oneline -5  # Find the commit you want
git checkout <commit-hash>
docker-compose up -d --build
```

### Production Considerations

**After configuring environment variables (see above), consider these additional steps:**

1. **Use a production WSGI server** - Replace Django dev server with gunicorn or uWSGI
2. **Set up HTTPS** - Use a reverse proxy (nginx, traefik, or Caddy) with Let's Encrypt
3. **Automated backups** - Set up cron job for regular database backups:
   ```bash
   # Add to crontab (daily backup at 2 AM)
   0 2 * * * docker run --rm -v productivity-application_journal_data:/data -v /path/to/backups:/backup ubuntu tar czf /backup/journal-backup-$(date +\%Y\%m\%d).tar.gz /data
   ```
4. **Monitor logs** - Set up log rotation and monitoring
5. **Consider PostgreSQL** - For multi-user deployments, migrate from SQLite to PostgreSQL
6. **Regular updates** - Pull and deploy updates regularly for security patches

## Running Tests

Run tests:
```bash
uv run pytest tests/
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=journal --cov-report=term-missing
```

## Code Quality

Format code:
```bash
uv run ruff check --select I --fix
uv run ruff format
```

Lint code:
```bash
uv run ruff check --fix
```

## Project Structure

```
.
├── journal_project/          # Django project settings
│   ├── settings.py           # Main Django configuration
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application
├── journal/                  # Main Django app
│   ├── models.py             # JournalEntry & UserProfile models
│   ├── views.py              # Views for auth and journal
│   ├── forms.py              # Django forms
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin configuration
│   ├── migrations/           # Database migrations
│   └── templates/journal/    # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── journal.html
│       └── partials/
│           ├── entries.html    # HTMX partial
│           └── entry_form.html # HTMX partial
├── static/
│   └── js/
│       └── htmx.min.js       # HTMX library
├── tests/                    # Unit tests
│   └── test_views.py
├── manage.py                 # Django management script
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
├── entrypoint.sh             # Docker entrypoint script
├── pyproject.toml            # Project dependencies (uv)
└── uv.lock                   # Locked dependencies
```

## Architecture

The application follows Django's MVT (Model-View-Template) architecture:

- **Models** (`journal/models.py`): JournalEntry model with user relationship
- **Views** (`journal/views.py`): Authentication and journal entry management
- **Templates** (`journal/templates/`): HTML with Tailwind CSS styling
- **HTMX Integration**: Dynamic content updates without full page reloads

### Key Design Decisions

1. **Tailwind CSS via CDN**: Simplifies setup, no build process needed
2. **HTMX**: Enables SPA-like experience with minimal JavaScript
3. **Django Built-in Auth**: Leverages Django's robust authentication system
4. **Modular Structure**: Easy to extend and refactor

## Usage

1. **Register**: Create a new account at `/register/`
2. **Login**: Sign in at `/login/`
3. **Write**: Enter your thoughts in the text area
4. **Save**: Click "Save Entry" to store your journal entry
5. **Browse**: Use the date picker to view entries from different dates
6. **Customize**: Click the hamburger menu (☰) to toggle theme or logout
7. **Admin**: Access admin panel at `/admin/` for data management

## API Endpoints

### Authentication
- `GET /login/` - Login page
- `POST /login/` - Login form submission
- `GET /register/` - Registration page
- `POST /register/` - Registration form submission
- `POST /logout/` - Logout

### Journal
- `GET /` - Main journal page (requires authentication)
- `POST /create-entry/` - Create new entry (HTMX endpoint)
- `GET /entries/?date=YYYY-MM-DD` - Get entries by date (HTMX endpoint)
- `POST /api/theme/update/` - Update user theme preference (light/dark/system)

## Security Notes

- Built-in Django authentication and CSRF protection
- Password hashing with Django's PBKDF2 algorithm
- Session-based authentication
- For production deployment:
  - Set `DEBUG = False`
  - Change `SECRET_KEY`
  - Configure `ALLOWED_HOSTS`
  - Use a production-grade database (PostgreSQL)
  - Serve static files properly

## Future Enhancements

Planned improvements:
- Entry editing and deletion
- Entry ratings/mood tracking
- Rich text editor (WYSIWYG)
- Entry search functionality
- Tags and categories
- Export to PDF/Markdown
- Entry statistics and insights (word count, streaks, etc.)
- Word cloud visualization
- Old entries highlighting
- Mobile app (using Django REST API)

## Development

To add new features:

1. Create/modify models in `journal/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Update views in `journal/views.py`
5. Create/update templates
6. Add URL patterns to `journal/urls.py`
7. Test thoroughly
8. Format code with ruff

## License

Personal use project. Created with the assistance of Claude AI. Used my myself locally on my home server.
