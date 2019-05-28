from django.urls import path, include

from . import views


# Set application namespace
# app_name = 'screendoor'

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_form, name='register'),
    path('login/', views.login_form, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accountcreated/', views.account_created, name='account_created'),
    path('confirm/', views.confirm_account, name='confirm_account'),
    path('createnewposition', views.import_position, name='importposition'),
]
