
from django.db import models
from django.urls import reverse


class Course(models.Model):
    STATUS_CHOICES = [
        ("published", "Published"),
        ("draft", "Draft"),
    ]

    CATEGORY_CHOICES = [
        ("programming", "Programming"),
        ("ai", "Artificial Intelligence"),
        ("web", "Web Development"),
        ("data", "Data Science"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    enrolled_count = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    cover_emoji = models.CharField(max_length=10, default="📚")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_launch", args=[self.pk])
class CourseHistory(models.Model):
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("published", "Published"),
        ("unpublished", "Moved to Draft"),
        ("deleted", "Deleted"),
    ]

    # Keep this record even if the original course is deleted.
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history",
    )
    course_title = models.CharField(max_length=200)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.course_title} - {self.get_action_display()}"
