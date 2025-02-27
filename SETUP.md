# Celery Setup Guide for IurisSoft

This guide covers the full setup of Celery for the IurisSoft project, ensuring smooth local development, environment variable management, and compatibility with future Celery versions.

---

## 1. Project Structure Overview

Ensure your project structure follows a standard format:

```
Iuris-Soft/
|-- core/
|   |-- __init__.py
|   |-- settings.py
|   |-- celery.py     # Ensure Celery app lives here
|-- cases/
|   |-- tasks.py      # Your Celery tasks
|-- .env              # Environment variables
|-- Makefile          # To manage Celery worker and beat
```

---

## 2. Environment Variables (.env)

Create a `.env` file with the following content:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
ADMINS=[('Superadmin', 'youremail@gmail.com')]
```

**NOTE:** For Gmail, you need to use an **App Password** if 2FA is enabled.

---

## 3. settings.py - Email & Celery Configuration

### Email Settings

```python
import ast

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
ADMINS = ast.literal_eval(os.getenv("ADMINS", "[]"))
```

### Celery Configuration

```python
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 100
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
```

---

## 4. core/celery.py

Ensure `celery.py` exists under `core` and is correctly setup:

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
```

---

## 5. cases/tasks.py

Sample task (make sure it matches the project layout):

```python
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def notify_upcoming_due_cases():
    send_mail(
        'Case Reminder',
        'This is a reminder for upcoming cases.',
        'from@example.com',
        ['lawyer@example.com']
    )
```

---

## 6. Makefile

Create a `Makefile` in the root directory to ease Celery management.

```make
.PHONY: celery-worker celery-beat

celery-worker:
	celery -A core.celery worker --loglevel=info

celery-beat:
	celery -A core.celery beat --loglevel=info
```

Run workers and beat with:

```bash
make celery-worker
make celery-beat
```

---

## 7. Management Command (send_due_cases)

Create management command under `cases/management/commands/send_due_cases.py`:

```python
from django.core.management.base import BaseCommand
from cases.tasks import notify_upcoming_due_cases

class Command(BaseCommand):
    help = 'Send notifications for upcoming due cases'

    def handle(self, *args, **kwargs):
        self.stdout.write("Running due cases notification task...")
        notify_upcoming_due_cases.delay()
        self.stdout.write(self.style.SUCCESS('Successfully triggered notifications'))
```

Run with:

```bash
./manage.py send_due_cases
```

---

## 8. Running Redis (Docker)

For development, you can run Redis with Docker:

```bash
docker run -d -p 6379:6379 redis
```

---

## 9. Common Errors & Fixes

### Task Not Registered

- Make sure `cases` is listed under `INSTALLED_APPS`.
- Ensure `@shared_task` is used correctly.
- Make sure `app.autodiscover_tasks()` works in `celery.py`.

### Gmail Authentication Errors

- Enable App Passwords in your Google Account.
- Use App Password instead of your regular password.

---

## 10. Future-Proof: Celery 6.0

Add this to prevent future compatibility issues:

```python
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
```

---

With this setup, you have:

✅ Proper email setup via Gmail  
✅ Celery fully integrated with Django  
✅ Makefile for simple worker management  
✅ Task discovery and registration working  
✅ Redis as the broker  

---

## Quick Start

```bash
# Start Redis
make celery-worker
make celery-beat

# Trigger case notifications
./manage.py send_due_cases
```

---

✅ You're all set! 🎉

