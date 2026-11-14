
from django.urls import path
from . import views

urlpatterns = [
    path("my-courses/", views.my_courses, name="my_courses"),
    path("courses/create/", views.create_course, name="create_course"),
    path("courses/<int:pk>/edit/", views.edit_course, name="edit_course"),
    path("courses/<int:pk>/delete/", views.delete_course, name="delete_course"),
    path("courses/<int:pk>/launch/", views.launch_course, name="course_launch"),
    path("python-course/", views.python_course, name="python_course"),
]
s