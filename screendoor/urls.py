from django.urls import path, include

from . import views

# Set application namespace
# app_name = 'screendoor'

urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.register_form, name='register'),
    path('login', views.login_form, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('confirm', views.login_form, name='confirm_account'),
    path('createnewposition', views.import_position, name='importposition'),
    path('positions', views.positions, name='positions'),
    path('positions/<sort_by>', views.sort_positions, name='sort_positions'),
    path('position/<str:reference>/<int:position_id>',
         views.position_detail, name='position'),
    path('position/<str:reference>/<int:position_id>/<uuid:task_id>',
         views.position_detail, name='position_upload'),
    path('position/<str:reference>/<int:position_id>/<str:sort_by>',
         views.sort_applicants, name='sort_applicants'),
    path('position/edit', views.edit_position, name='edit'),
    path('position/delete', views.delete_position, name='delete'),
    path('position/upload-applications',
         views.upload_applications, name='upload-applications'),
    path('application/<app_id>', views.application, name='application'),
    path('progress/<task_id>', views.task_status, name='task_status'),
    path('nlp/', views.nlp,
         name='nlp')
]
