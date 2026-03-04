# zsh commands

ruff format # code formatting
ruff check --fix # linting

ruff check --select i --fix
ruff format # need to execute both to sort imports


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
- ✅ Theme toggle (light/dark mode with hamburger menu)
- ✅ Hamburger menu navigation (username, theme toggle, logout)
- ✅ Mobile-responsive design
- ✅ Docker deployment support
- ✅ Unit tests for views

## UI/Navigation Details
- **Hamburger menu** in header (all screen sizes) contains:
  - Username display
  - Theme toggle switch (sun/moon icons)
  - Logout button
- Theme toggle auto-detects current theme and flips between light/dark
- New users default to system preference (respects OS dark mode setting)
- Menu closes on click-outside or Escape key

# Features to Add

- Tags and categories, ideally LLM-powered but my server is CPU only, so see if there's a small LLM that would work.
  - It would analyse and tag new entries (user can edit the tags if they want maybe), or keep tags completely hidden, not sure.
- Export user data as JSON, and allow import from JSON as well.
- I want analysis of my existing entries, and then recommendations/messages back on what to do based on the feedback.
  - A sort of tailored life coaching?
  - e.g. if a lot of my journal entries are about frustrations at work, then maybe suggestion/motivation to apply for jobs, highlighting how long I've been frustrated?
- Voice to text would be good eventually.
