
from django.db import models


class Workshop(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=100, default="General")
    instructor = models.CharField(max_length=120)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    capacity = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    meeting_url = models.URLField(blank=True)
    recording_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="upcoming",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title

    @property
    def is_free(self):
        return self.price == 0

    @property
    def registered_count(self):
        return self.registrations.count()

    @property
    def seats_remaining(self):
        return max(0, self.capacity - self.registered_count)


class WorkshopRegistration(models.Model):
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    student_name = models.CharField(max_length=120)
    student_email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        ordering = ["-registered_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workshop", "student_email"],
                name="unique_workshop_student_email",
            )
        ]

    def __str__(self):
        return f"{self.student_name} - {self.workshop.title}"


class WorkshopHistory(models.Model):
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history",
    )
    workshop_title = models.CharField(max_length=200)
    action = models.CharField(max_length=40)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.workshop_title} - {self.action}"
