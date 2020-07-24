from django.urls import include, path

from .views import classroom, students, teachers

urlpatterns = [
    path('', classroom.home, name='home'),
    path('contact_us/', classroom.contactView, name='contact_us'),
    path('success_send/', classroom.successView, name='success_send'),
    path('select_signupview/', classroom.selectSignUpView, name='select_signup_view'),
    path('change_password/', classroom.change_password,name= 'change_password'),
    path('edit_profile/', classroom.profile,name= 'edit_profile'),
    path('our_team/', classroom.aboutTeams, name='about_Teams'),
        
    path('students/', include(([
        path('', students.search_individual, name = "search_individual"),
        path('search_individual_details/', students.search_individual_details, name = "search_individual_details"),

    ], 'classroom'), namespace='students')),

    path('teachers/', include(([
        path('', teachers.index, name = "attendance_index"),
        path('add-student/', teachers.add_student , name = "attendance_add_student"),

        path('dataset_creator/', teachers.dataset_creator, name = "dataset_creator"),
        path('detector/', teachers.detector, name = "attandance_detector"),

        path('search_attendance/', teachers.search_attendance, name = "search_attendance"),
        path('search_attendance_date/', teachers.search_attendance_date, name = "search_attendance_date"),
        path('search_attendance_details/', teachers.search_attendance_details, name = "search_attendance_details"),

    ], 'classroom'), namespace='teachers')),
]
