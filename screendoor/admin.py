from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ScreenDoorUserCreationForm
from .models import *


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 0


class QuestionInline(admin.StackedInline):
    model = FormQuestion
    extra = 0


class PositionAdmin(admin.ModelAdmin):
    inlines = [RequirementInline]


class ApplicantAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


admin.site.register(FormQuestion)
admin.site.register(RequirementMet)
admin.site.register(Stream)
admin.site.register(Classification)
admin.site.register(Education)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Requirement)
admin.site.register(Position, PositionAdmin)
admin.site.register(EmailAuthenticateToken)


class PositionInline(admin.TabularInline):
    model = ScreenDoorUser.positions.through
    extra = 0


class AccountTokenInline(admin.TabularInline):
    model = EmailAuthenticateToken
    extra = 0


class ScreenDoorUserAdmin(UserAdmin):
    add_form = ScreenDoorUserCreationForm
    model = ScreenDoorUser
    list_display = ['email', ]
    inlines = [PositionInline, AccountTokenInline]


admin.site.register(ScreenDoorUser, ScreenDoorUserAdmin)
