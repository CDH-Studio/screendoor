from celery import shared_task
from datetime import datetime, timedelta
from .models import EmailAuthenticateToken, Position

# Notes
# Backends use resources to store and transmit results. To ensure that resources are released, you must eventually call get() or forget() on EVERY AsyncResult instance returned after calling a task.

# Triggered tasks


# Scheduled tasks

# Once per day
@shared_task
def delete_authorization_tokens():
    EmailAuthenticateToken.objects.filter(
        created=datetime.now() - timedelta(days=2)).delete()


# Once per day
@shared_task
def delete_orphaned_positions():
    Position.objects.filter(screendooruser=None).delete()
