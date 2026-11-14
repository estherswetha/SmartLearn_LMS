from django.contrib import admin
from .models import LessonVideo


@admin.register(LessonVideo)
class LessonVideoAdmin(admin.ModelAdmin):
    list_display = ("lesson_name", "video", "uploaded_at")