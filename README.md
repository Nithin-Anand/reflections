# Personal Journal Application

A web-based personal journal application with a clean, modern design, built with Django, Tailwind CSS, and HTMX.

## Features

- User authentication (login/registration)
- Write and save journal entries with timestamps
- Calendar date picker to view entries by date
- Clean, modern UI design with Tailwind CSS
- Dynamic content updates with HTMX (no page reloads)
- SQLite database for local storage
- Django admin interface for data management
- Responsive design for desktop and mobile

## Tech Stack

- **Backend**: Django 6.0
- **Frontend**: Tailwind CSS 3.x (CDN) + HTMX
- **Database**: SQLite3
- **Testing**: pytest with 100% coverage (for database layer)
- **Code Quality**: Ruff formatter and linter

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

## Migrating Data from NiceGUI Version

If you have data from the previous NiceGUI version, run the migration script:

```bash
uv run python migrate_old_data.py
```

**Note:** Migrated users will have temporary passwords. Reset them via the Django admin interface at `http://localhost:8000/admin/`

## Running Tests

Run database layer tests:
```bash
uv run pytest tests/
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=database --cov=auth_service --cov-report=term-missing
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
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── journal/                  # Main Django app
│   ├── models.py             # JournalEntry model
│   ├── views.py              # Views for auth and journal
│   ├── forms.py              # Django forms
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin configuration
│   └── templates/journal/    # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── journal.html
│       └── partials/
│           └── entries.html  # HTMX partial
├── static/
│   └── js/
│       └── htmx.min.js       # HTMX library
├── database/                 # Old database (backup)
│   ├── client.py             # Legacy code
│   └── main.db               # Old SQLite database
├── tests/                    # Unit tests
├── migrate_old_data.py       # Data migration script
├── manage.py                 # Django management script
└── pyproject.toml            # Project dependencies
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

Possible improvements:
- Entry editing and deletion
- Rich text editor
- Entry search functionality
- Tags and categories
- Export to PDF/Markdown
- Dark mode toggle
- Entry statistics and insights
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
