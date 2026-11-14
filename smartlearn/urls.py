
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from accounts.views import scorm_catalogue
from django.urls import path, include
from django.views.generic import RedirectView
# ACCOUNTS VIEWS
from accounts.views import (
    login_page,
    dashboard,
    module_page,
    all_modules,
    lesson1,
    translate_text,
    summary_ai,
    summary_ai_api,
    notes_ai_api,
    tutor_ai,
    tutor_ai_api,
    adaptive_ai,
    adaptive_ai_api,
    quiz_ai,
    quiz_ai_api,
    gamification,
    quiz_ai_submit,
    quiz_history_api,
    gamification_api,
    knowledge_quest_api,
    knowledge_quest_submit,
    voice_ai_api,
    learntwin_api,
    learntwin,
    scorm_catalogue,
)

# COURSES VIEWS
from courses.views import (
    my_courses,
    python_course,
    create_course,
    edit_course,
    delete_course,
    launch_course,
    course_history,
)

# VIDEOS VIEWS
from videos.views import (
    generate_transcript,
)

urlpatterns = [
    # ADAPTIVE AI
    path("adaptive-ai/", adaptive_ai, name="adaptive_ai"),
    path("adaptive-ai/api/", adaptive_ai_api, name="adaptive_ai_api"),

    # QUIZ AI
    path("quiz-ai/", quiz_ai, name="quiz_ai"),
    path("quiz-ai/api/", quiz_ai_api, name="quiz_ai_api"),
    path("quiz-ai/submit/", quiz_ai_submit, name="quiz_ai_submit"),

    # QUIZ HISTORY
    path("quiz-history/api/", quiz_history_api, name="quiz_history_api"),

    # TUTOR AI
    path("tutor-ai/", tutor_ai, name="tutor_ai"),
    path("tutor-ai/api/", tutor_ai_api, name="tutor_ai_api"),

    # NOTES AI
    path("notes-ai/api/", notes_ai_api, name="notes_ai_api"),

    # SUMMARY AI
    path("summary-ai/", summary_ai, name="summary_ai"),
    path("summary-ai/api/", summary_ai_api, name="summary_ai_api"),

    # VIDEO AI
    path(
        "video-ai/transcribe/",
        generate_transcript,
        name="generate_transcript",
    ),

    # GAMIFICATION
    path("gamification/", gamification, name="gamification"),
    path("gamification/api/", gamification_api, name="gamification_api"),

    # KNOWLEDGE QUEST
    path(
        "knowledge-quest/api/",
        knowledge_quest_api,
        name="knowledge_quest_api",
    ),
    path(
        "knowledge-quest/submit/",
        knowledge_quest_submit,
        name="knowledge_quest_submit",
    ),

    # VOICE AI
    path("voice-ai/api/", voice_ai_api, name="voice_ai_api"),

    # LEARNTWIN AI
    path("learntwin/", learntwin, name="learntwin"),
    path("learntwin/api/", learntwin_api, name="learntwin_api"),

    # TRANSLATION
    path("translate/", translate_text, name="translate_text"),

    # COURSES
    path("python-course/", python_course, name="python_course"),
    path("my-courses/", my_courses, name="my_courses"),

    # CREATE COURSE
    path(
        "courses/create/",
        create_course,
        name="create_course",
    ),

    # EDIT COURSE
    path(
        "courses/<int:pk>/edit/",
        edit_course,
        name="edit_course",
    ),

    # DELETE COURSE
    path(
        "courses/<int:pk>/delete/",
        delete_course,
        name="delete_course",
    ),
    
    # LAUNCH COURSE
    path(
        "courses/<int:pk>/launch/",
        launch_course,
        name="course_launch",
    ),
    path(
    "scorm-courses/",
    scorm_catalogue,
    name="scorm_catalogue"
),
    path("course-history/", course_history, name="course_history"),
    # LESSONS
    path("lesson1/", lesson1, name="lesson1"),
    path("assessments/", include("assessments.urls")),
    path(
    "module/assessments/",
    RedirectView.as_view(url="/assessments/", permanent=False),
    name="module_assessments"
    ),
    # MODULES
    path("module/<str:module>/", module_page, name="module_page"),
    path("modules/", all_modules, name="all_modules"),

    # LOGIN AND DASHBOARD
    path("", login_page, name="login"),
    path("dashboard/", dashboard, name="dashboard"),

    # ADMIN
    path("admin/", admin.site.urls),
    path("workshops/", include("workshops.urls")),
    path("accounts/", include("accounts.urls")),
    
]  


# MEDIA FILES (DEVELOPMENT ONLY)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
