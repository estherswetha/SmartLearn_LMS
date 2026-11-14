
from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path("", views.assessment_dashboard, name="dashboard"),
    path("create/", views.create_assessment, name="create"),
     path(
        "<int:pk>/",
        views.assessment_detail,
        name="detail"
    ),

    path(
        "<int:pk>/add-question/",
        views.add_question,
        name="add_question"
    ),

    path(
        "question-bank/",
        views.question_bank,
        name="question_bank"
    ),

    path("question-bank/", views.question_bank, name="question_bank"),
    path("tags/", views.assessment_tags, name="tags"),
    path("tags/<int:pk>/delete/", views.delete_tag, name="delete_tag"),

    path("summary/", views.assessment_summary, name="summary"),
    path("archived/", views.archived_assessments, name="archived"),
    path("export/questions/", views.export_question_bank, name="export_questions"),

    path("<int:pk>/", views.assessment_detail, name="detail"),
    path("<int:pk>/archive/", views.archive_assessment, name="archive"),
    path("<int:pk>/restore/", views.restore_assessment, name="restore"),
]
