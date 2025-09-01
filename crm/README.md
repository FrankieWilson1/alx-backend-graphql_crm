````markdown
# CRM Application Celery Setup

This document explains how to set up and run the Celery worker and scheduler for managing background and periodic tasks.

## Prerequisites

- **Redis:** Celery uses Redis as a message broker. Ensure Redis is installed and running on your system.

### Installation (Ubuntu):
```bash
sudo apt update
sudo apt install redis-server
```

### Check status:
```bash
sudo systemctl status redis-server
```

## Installation

1. **Install dependencies:** Make sure all required packages, including `celery`, `django-celery-beat`, and `redis`, are installed.
```bash
pip install -r requirements.txt
```

## Database Migrations

Celery Beat requires its own database tables to manage the schedule. Run migrations to create them.

```bash
python manage.py migrate
```

## Running Celery

You need to run two separate processes: a worker to execute tasks and a scheduler (Celery Beat) to send tasks based on the schedule.

### Start the Celery Worker:
This command starts the worker, which listens for tasks from the message broker and executes them. The `-l info` flag sets the log level to informational.
```bash
celery -A crm worker -l info
```

### Start the Celery Beat Scheduler:
This command starts the scheduler, which checks the configured schedules and adds tasks to the queue at the appropriate times.
```bash
celery -A crm beat -l info
```

## Verification

To confirm that the report generation task is working, check the log file after the scheduled time.

### Check the logs:
```bash
cat /tmp/crm_report_log.txt
```

You should see a new entry with the generated report every Monday at 6:00 AM.
````