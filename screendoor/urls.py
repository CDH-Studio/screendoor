from django.urls import path, include

from . import views


# Set application namespace
# app_name = 'screendoor'

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_form, name='register'),
    path('login/', views.login_form, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('confirm/', views.login_form, name='confirm_account'),
    path('createnewposition/', views.import_position, name='importposition'),
    path('positions/', views.positions, name='positions'),
    path('position/', views.position, name='position'),
    path('importapplications/', views.import_applications,
         name='importapplications'),
]
