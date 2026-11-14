from django.db import models
from django.contrib.auth.models import User


class ScormCourse(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    package = models.FileField(upload_to="scorm_packages/")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_scorm_courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
