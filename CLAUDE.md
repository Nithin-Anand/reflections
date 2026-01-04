# zsh commands

ruff format # Code formatting
ruff check --fix # linting

ruff check --select I --fix
ruff format # Need to execute both to sort imports


# Code Style

Follow Python pep8 guidelines
Use ruff to format
Use OOP, follow best principles, code should be maintainable
Ensure effective unit testing and code coverage
Favour modularity, code reuse and testability

# Tech Stack

- **Backend**: Django 5.x (Python web framework)
- **Frontend**: Tailwind CSS 3.x + HTMX for dynamic interactions
- **Database**: SQLite3
- **Deployment**: Docker with docker-compose
- **Testing**: pytest with pytest-django
- **Code Quality**: Ruff (formatting and linting)

# Program Requirements

This program is a personal journal app that can be deployed locally or on home server.
- Users should be able to access the app via a browser. 
- Users should be able to enter, into a text box, their thoughts/for journalling. 
- There should be a calendar widget that allows users to select a day and see all their entries for that day. 
- The design should be clear, maybe slightly vintage looking (evoking feeling of a diary).
- The database schema for the journal entry should save both a timestamp and the diary entry.
- Secure authentication should be supported

# Current Implementation Status

The application is built with Django following MVT architecture:
- ✅ User authentication (login/registration)
- ✅ Journal entry creation with timestamps
- ✅ Calendar date picker for viewing entries by date
- ✅ Modern, clean UI with Tailwind CSS
- ✅ Dynamic updates with HTMX (no page reloads)
- ✅ Theme toggle (light/dark mode)
- ✅ Docker deployment support
- ✅ Unit tests for views

# Features to Add

- Entry deletion
- Entry editing
- Entry ratings/mood tracking
- Old entries highlighting (visual indicators for age)
- Word cloud visualization
- Rich text formatting (WYSIWYG editor)
- Entry search functionality
- Tags and categories
- Export to PDF/Markdown