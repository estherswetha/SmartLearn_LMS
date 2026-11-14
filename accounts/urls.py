from django.urls import path
from . import views

urlpatterns = [
    path(
        "register/",
        views.register_student,
        name="register_student"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "student-home/",
        views.student_home,
        name="student_home"
    ),

    path(
        "instructor-home/",
        views.instructor_home,
        name="instructor_home"
    ),

    path(
        "scorm-upload/",
        views.upload_scorm_course,
        name="upload_scorm_course"
    ),
]