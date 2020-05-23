from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = "attendance_index"),
    path('add-student/', views.add_student , name = "attendance_add_student"),
    path('detector/', views.detector, name = "attandance_detector"),
    path('dataset_creator/', views.dataset_creator, name = "dataset_creator"),
    path('individual_details/', views.individual_details, name = "individual_details"),
    path('individual/', views.individual, name = "individual"),
    # path('', views., name=""),
]