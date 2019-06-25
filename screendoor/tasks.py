from celery import shared_task
from datetime import datetime, timedelta
from .models import EmailAuthenticateToken, Position

# Notes
# Backends use resources to store and transmit results. To ensure that resources are released, you must
# eventually call get() or forget() on EVERY AsyncResult instance returned after calling a task.
# Information about currently executing task can be accessed like:
# function_name.request.
# e.g.
# function_name.request.id
# or, if the function is annotated with (bind=True), use self.
# You should pass self into the function in this case.
# Get ID in the view when you call a task function, and then pass it to the
# template so it can be a accessed via the JS function to poll for results.


# Triggered tasks

@shared_task(bind=True)
def process_position(self):
    pass

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
