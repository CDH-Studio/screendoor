from django.contrib.auth.models import AbstractUser
from django.db import models


class ScreenDoorUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)

    def confirm_email(self):
        self.email_confirmed = True
