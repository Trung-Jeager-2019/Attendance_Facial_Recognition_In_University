from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="attendance_index"),
    path('add-student/', views.add_student , name="attendance_add_student"),
    # path('detect/', views., name="attendance_detect"),
]