# Personal Journal Application

A web-based personal journal application with a clean, modern design, built with Django, Tailwind CSS, and HTMX.

## Features

- User authentication (login/registration)
- Write and save journal entries with timestamps
- Calendar date picker to view entries by date
- Clean, modern UI design with Tailwind CSS
- Theme toggle (light/dark mode)
- Dynamic content updates with HTMX (no page reloads)
- SQLite database for local storage
- Django admin interface for data management
- Responsive design for desktop and mobile
- Docker support for easy deployment

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Tailwind CSS 3.x (CDN) + HTMX
- **Database**: SQLite3
- **Testing**: pytest with pytest-django
- **Code Quality**: Ruff formatter and linter
- **Deployment**: Docker with docker-compose

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

## Docker Deployment

### Using Docker Compose (Recommended)

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

Data is persisted in a Docker volume named `journal_data`.

### Environment Variables

Create a `.env` file for production deployment:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Production Considerations

For production deployment:
1. Set `DJANGO_DEBUG=False`
2. Use a strong `DJANGO_SECRET_KEY`
3. Configure `DJANGO_ALLOWED_HOSTS` with your domain
4. Consider using a production WSGI server (e.g., gunicorn)
5. Set up HTTPS with a reverse proxy (nginx/traefik)
6. Consider migrating to PostgreSQL for better performance
7. Set up automated backups of the database volume

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
6. **Admin**: Access admin panel at `/admin/` for data management

## API Endpoints

### Authentication
- `GET /login/` - Login page
- `POST /login/` - Login form submission
- `GET /register/` - Registration page
- `POST /register/` - Registration form submission
- `GET /logout/` - Logout

### Journal
- `GET /` - Main journal page (requires authentication)
- `POST /create-entry/` - Create new entry (HTMX endpoint)
- `GET /entries/?date=YYYY-MM-DD` - Get entries by date (HTMX endpoint)

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
