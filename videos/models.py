from django.db import models


class LessonVideo(models.Model):
    lesson_name = models.CharField(max_length=200)

    video = models.FileField(upload_to="lessons/")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.lesson_name
# Create your models here.
