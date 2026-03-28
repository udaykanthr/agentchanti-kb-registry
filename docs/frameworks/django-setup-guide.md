---
id: "doc-016"
title: "Django Project Setup and Bootstrap Guide"
category: "doc"
language: "python"
version: "1.0.0"
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

## 1. Prerequisites and Virtual Environment

It is a best practice to install Django within an isolated Python virtual environment.

```bash
# Create a new directory for your project
mkdir my_django_project
cd my_django_project

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

Your directory structure should now look like this:
```
my_django_project/
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
python manage.py startapp myapp
```

**Important:** You must register your new app in `config/settings.py` under the `INSTALLED_APPS` list:

```python
# config/settings.py

INSTALLED_APPS = [
    # ... default django apps ...
    'django.contrib.staticfiles',
    
    # Local apps
    'myapp',
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

## Typical Next Steps
- Define your models in `myapp/models.py`.
- Register your models in `myapp/admin.py` to manage them in the admin dashboard.
- Create views in `myapp/views.py` and map them to URLs via `myapp/urls.py`.
- Add a `.gitignore` file to ignore the `venv/` directory, `db.sqlite3` file, and `__pycache__` folders before committing to version control.
