from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = "attendance_index"),
    path('add-student/', views.add_student , name = "attendance_add_student"),

    path('dataset_creator/', views.dataset_creator, name = "dataset_creator"),
    path('detector/', views.detector, name = "attandance_detector"),

    path('search_attendance/', views.search_attendance, name = "search_attendance"),
    path('search_attendance_details/', views.search_attendance_details, name = "search_attendance_details"),

    path('search_individual/', views.search_individual, name = "search_individual"),
    path('search_individual_details/', views.search_individual_details, name = "search_individual_details"),
]