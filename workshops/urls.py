
from django.urls import path
from . import views

urlpatterns = [
    path("", views.workshop_list, name="workshop_list"),
    path("create/", views.create_workshop, name="create_workshop"),
    path("<int:pk>/", views.workshop_detail, name="workshop_detail"),
    path("<int:pk>/register/", views.register_workshop, name="register_workshop"),
    path("<int:pk>/cancel/", views.cancel_registration, name="cancel_registration"),
    path("<int:pk>/join/", views.join_workshop, name="join_workshop"),
    path(
        "<int:pk>/attendance/<int:registration_id>/",
        views.update_attendance,
        name="update_workshop_attendance",
    ),
    path("<int:pk>/complete/", views.complete_workshop, name="complete_workshop"),
    path("history/", views.workshop_history, name="workshop_history"),
]
