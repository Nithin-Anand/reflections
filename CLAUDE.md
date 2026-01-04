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

Python for back-end
For the front-end, I'm not sure where to use something simple like nicegui or use Django and proper web frameworks. Please determine best course of action. Consider scalability, how nice the UI can look, performance and maintainability
sqlite3 for the database
Containerise via Docker (not needed first)

# Program Requirements

This program is a personal journal app that can be deployed locally or on home server.
- Users should be able to access the app via a browser. 
- Users should be able to enter, into a text box, their thoughts/for journalling. 
- There should be a calendar widget that allows users to select a day and see all their entries for that day. 
- The design should be clear, maybe slightly vintage looking (evoking feeling of a diary).
- The database schema for the journal entry should save both a timestamp and the diary entry.
- Secure authentication should be supported

# Workflow

1. Based on the requirements, determine how the front-end should be created. Check with user before proceeding.
2. Create the backend code for connecting to the database, inserting new entries, reading, committing etc.
3. Proceed based on what Claude thinks should be created next.


# Features to add

- Delete entries
- Ratings
- Dark mode
- Better UI
- Old entries highlighting
- Word cloud
- Rich text formatting