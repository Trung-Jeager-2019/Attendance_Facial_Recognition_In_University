from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="attendance_index"),
    path('detect/', views., name="attendance_detect"),
]