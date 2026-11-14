# ADD THIS MODEL BELOW YOUR EXISTING MODELS IN quizzes/models.py

from django.db import models


class QuizHistory(models.Model):
    subject = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=50)
    mode = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    questions = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.topic} - {self.score}/{self.total_questions}"
