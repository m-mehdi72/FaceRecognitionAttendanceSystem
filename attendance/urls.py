from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.index, name='index'),
    path('mark-attendance/', views.mark_attendance, name='mark-attendance'),
    path('download-attendance/', views.download_attendance, name='download-attendance'),
]
