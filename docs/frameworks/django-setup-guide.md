---
id: "doc-016"
title: "Django Project Setup and Bootstrap Guide"
category: "doc"
language: "python"
version: "1.1.0"
created_at: "2026-03-28"
tags:
  - django
  - setup
  - bootstrap
  - cli
  - web
---

# Django Project Setup and Bootstrap Guide

This guide covers the end-to-end process of bootstrapping a new Django application, from installation to running the local development server.

> **IMPORTANT — use the task's project name, not a hardcoded placeholder.**
> Every `<project_name>` and `<app_name>` below must be replaced with the name
> derived from the user's task description.  NEVER use `my_django_project` or
> `myapp` verbatim unless the user explicitly requested those names.

## 1. Prerequisites and Virtual Environment

It is a best practice to install Django within an isolated Python virtual environment.

```bash
# Replace <project_name> with the actual project name from the task
mkdir <project_name>
cd <project_name>

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

## 2. Django Installation

With the virtual environment activated, install Django using `pip`:

```bash
pip install django
```

To verify the installation and check the version:

```bash
python -m django --version
```

## 3. Initializing the Project

Create the foundational Django project structure. The `.` at the end tells Django to install the project in the current directory instead of nesting it.

```bash
# Replace 'config' with your preferred project name (e.g., core, app_name)
django-admin startproject config .
```

Your directory structure should now look like this (using `<project_name>` as the root):
```
<project_name>/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── venv/
```

## 4. Initializing an Application

Django projects are composed of multiple distinct "apps". Create your first app using `manage.py`:

```bash
# Replace <app_name> with a name derived from the task (e.g. 'blog', 'api', 'users')
python manage.py startapp <app_name>
```

**Important:** You must register your new app in `config/settings.py` under the `INSTALLED_APPS` list:

```python
# config/settings.py

INSTALLED_APPS = [
    # ... default django apps ...
    'django.contrib.staticfiles',

    # Local apps
    '<app_name>',
]
```

## 5. Database Setup and Migrations

Django comes with a built-in SQLite database by default. Before running the server, you need to apply the default migrations (for admin, auth, sessions, etc.).

```bash
# Create migration files based on model changes
python manage.py makemigrations

# Apply migrations to the database
python manage.py migrate
```

## 6. Creating a Superuser

To access the Django admin interface (`/admin/`), create a local superuser account:

```bash
python manage.py createsuperuser
```
Follow the prompts to set your username, email, and password.

## 7. Running the Development Server

Start the local development server to test your application:

```bash
python manage.py runserver
```

You can now visit your app in the browser:
- **Application Preview:** `http://127.0.0.1:8000/`
- **Admin Interface:** `http://127.0.0.1:8000/admin/`

## 8. Test File Organisation — Avoid `tests.py` vs `tests/` Conflict

`python manage.py startapp <app_name>` creates a stub `<app_name>/tests.py`.  If you later
organise tests in a **subdirectory** (`<app_name>/tests/test_views.py`), you must
remove the stub first — otherwise Python's import system raises:

```
ImportError: 'tests' module incorrectly imported from '…/<app_name>/tests'.
Expected '…/<app_name>'. Is this module globally installed?
```

**Option A — Single test file (simple projects):** keep `<app_name>/tests.py` and write
all tests there.

**Option B — Tests subdirectory:** delete the stub and create the package:

```bash
rm <app_name>/tests.py
mkdir <app_name>/tests
touch <app_name>/tests/__init__.py
```

Then place test files inside `<app_name>/tests/` (e.g. `test_views.py`, `test_models.py`).

> Django discovers `tests/` packages automatically; the `__init__.py` is required
> so Python treats the directory as a regular package, not a namespace package.

## Typical Next Steps
- Define your models in `<app_name>/models.py`.
- Register your models in `<app_name>/admin.py` to manage them in the admin dashboard.
- Create views in `<app_name>/views.py` and map them to URLs via `<app_name>/urls.py`.
- Add a `.gitignore` file to ignore the `venv/` directory, `db.sqlite3` file, and `__pycache__` folders before committing to version control.
