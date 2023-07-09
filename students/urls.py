from django.urls import path
from . import views

urlpatterns = [
    path('login_user', views.login_user, name = "login"),
    path('student_panel', views.student_panel, name="s_panel"),
]