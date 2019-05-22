from django.urls import path

from . import views


# Set application namespace
# app_name = 'screendoor'

urlpatterns = [
    path('', views.index, name='index'),
]

# Example URL patterns
# urlpatterns = [
#    # ex: /polls/
#    path('', views.index, name='index'),
#    # ex: /polls/5/
#    path('<int:question_id>/', views.detail, name='detail'),
#    # ex: /polls/5/results/
#    path('<int:question_id>/results/', views.results, name='results'),
#    # ex: /polls/5/vote/
#    path('<int:question_id>/vote/', views.vote, name='vote'),
# ]
