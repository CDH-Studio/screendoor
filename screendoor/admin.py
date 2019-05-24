from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ScreenDoorUserCreationForm, ScreenDoorUserChangeForm
from .models import ScreenDoorUser


class ScreenDoorUserAdmin(UserAdmin):
    add_form = ScreenDoorUserCreationForm
    form = ScreenDoorUserChangeForm
    model = ScreenDoorUser
    list_display = ['email', ]


admin.site.register(ScreenDoorUser, ScreenDoorUserAdmin)
