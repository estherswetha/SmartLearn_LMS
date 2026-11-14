
from django.db import models
from django.conf import settings
import uuid


# ==========================================
# 1. ASSESSMENT TAG
# ==========================================

class AssessmentTag(models.Model):

    name = models.CharField(max_length=60)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_tags"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "created_by"],
                name="unique_assessment_tag_per_user"
            )
        ]

    def __str__(self):
        return self.name


# ==========================================
# 2. ASSESSMENT
# ==========================================

class Assessment(models.Model):

    ASSESSMENT_TYPES = [
        ("mcq", "Multiple Choice"),
        ("true_false", "True / False"),
        ("descriptive", "Descriptive"),
        ("coding", "Coding"),
        ("mixed", "Mixed Assessment"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("closed", "Closed"),
    ]

    QUESTION_COUNT_CHOICES = [
        (10, "10 Questions"),
        (50, "50 Questions"),
    ]

    title = models.CharField(max_length=200)

    assessment_type = models.CharField(
        max_length=20,
        choices=ASSESSMENT_TYPES,
        default="mcq"
    )

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    auto_evaluate = models.BooleanField(default=True)

    duration = models.PositiveIntegerField(default=30)

    extra_retakes = models.PositiveIntegerField(default=0)

    randomize_questions = models.BooleanField(default=False)

    question_count = models.PositiveSmallIntegerField(
        choices=QUESTION_COUNT_CHOICES,
        default=10
    )

    post_message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    archived = models.BooleanField(default=False)

    tags = models.ManyToManyField(
        AssessmentTag,
        blank=True,
        related_name="assessments"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assessments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==========================================
# 3. QUESTION
# ==========================================

class Question(models.Model):

    QUESTION_TYPES = [
        ("mcq", "Multiple Choice"),
        ("true_false", "True / False"),
        ("short", "Short Answer"),
        ("long", "Descriptive Answer"),
        ("coding", "Coding Challenge"),
        ("fill", "Fill in the Blanks"),
        ("matching", "Match the Following"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default="mcq"
    )

    # Stores MCQ options, matching pairs, etc.
    options = models.JSONField(
        default=list,
        blank=True
    )

    # Correct answer is only for teacher-side evaluation.
    # Never expose it through student-facing pages or APIs.
    correct_answer = models.TextField(blank=True)

    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text[:70]


# ==========================================
# 4. ASSESSMENT ASSIGNMENT
# ==========================================

class AssessmentAssignment(models.Model):

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_assignments"
    )

    # Unique link for each assigned student
    access_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    email_sent = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "student"],
                name="unique_assessment_student"
            )
        ]

    def __str__(self):
        return f"{self.assessment.title} - {self.student}"


# ==========================================
# 5. STUDENT ATTEMPT
# ==========================================

class Attempt(models.Model):

    assignment = models.ForeignKey(
        AssessmentAssignment,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    # Questions selected for this attempt
    questions = models.ManyToManyField(
        Question,
        blank=True,
        related_name="test_attempts"
    )

    started_at = models.DateTimeField(auto_now_add=True)

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    score = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ("in_progress", "In Progress"),
            ("submitted", "Submitted"),
            ("evaluated", "Evaluated"),
        ],
        default="in_progress"
    )

    def __str__(self):
        return f"Attempt {self.pk}"


# ==========================================
# 6. STUDENT ANSWERS
# ==========================================

class Answer(models.Model):

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    answer_text = models.TextField(blank=True)

    marks_awarded = models.FloatField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_attempt_question"
            )
        ]

    def __str__(self):
        return f"Answer for Question {self.question_id}"
