from django.urls import path

from screendoor.views.base_views import index, register_form, login_form, logout_view, login_form
from screendoor.views.main_views import positions, position_detail, position_detail_with_upload_error, delete_position, application, render_pdf
from screendoor.views.helper_views import sort_positions, sort_applicants, filter_applicants
from screendoor.views.import_pdfs import upload_applications, import_position, task_status
from screendoor.views.ajax_paths import change_favourites_status, add_user_to_position, remove_user_from_position, add_note, remove_note, edit_position

# Set application namespace
# app_name = 'screendoor'

urlpatterns = [
     # Base views
     path('', index, name='home'),
     path('register', register_form, name='register'),
     path('login', login_form, name='login'),
     path('logout', logout_view, name='logout'),
     path('confirm', login_form, name='confirm_account'),

     # Main views
     path('positions', positions, name='positions'),
     path('position/<str:reference>/<int:position_id>',
          position_detail,
          name='position'),
     path('position/delete', delete_position, name='delete'),
     path('application/<app_id>', application, name='application'),
     path('sbr_pdf/<app_id>', render_pdf, name='sbr'),

     # Helper views
     path('positions/<sort_by>', sort_positions, name='sort_positions'),
     path('position/<str:reference>/<int:position_id>/sort/<str:sort_by>',
          sort_applicants,
          name='sort_applicants'),
     path('position/<str:reference>/<int:position_id>/filter/<str:applicant_filter>',
          filter_applicants,
          name='filter_applicants'),
     
     # Import PDF views
     path('position/<str:reference>/<int:position_id>/<uuid:task_id>',
          position_detail,
          name='position_upload'),
     path('position/upload-applications',
          upload_applications,
          name='upload-applications'),     
     path('createnewposition', import_position, name='importposition'),
     path('progress/<task_id>', task_status, name='task_status'),
     
     # Ajax URL views
     path('change_favourites_status',
          change_favourites_status,
          name='change_favourites_status'),
     path('add_user_to_position',
          add_user_to_position,
          name='add_user_to_position'),
     path('remove_user_from_position',
          remove_user_from_position,
          name='remove_user_from_position'),
     path('add_note', add_note, name='add_note'),
     path('remove_note', remove_note, name='remove_note'),
     path('edit-position', edit_position, name='edit-position')
]
