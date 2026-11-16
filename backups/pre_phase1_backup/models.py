from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

# simple email-first user (dev)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class QuizSet(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    session_only = models.BooleanField(default=False)  # True = live-added, never shown in Library

    class Meta:
        permissions = [
            ("manage_quizzes", "Can create/update/delete quizzes and questions"),
            ("view_reports", "Can view quiz performance reports"),
        ]

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(QuizSet, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    timer_seconds = models.IntegerField(default=20)
    order = models.IntegerField(default=0)
    image = models.TextField(null=True, blank=True)  # Store base64 encoded image data

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)  # Store base64 encoded image data

    def __str__(self):
        return self.text

class QuizSession(models.Model):
    STATE_WAITING = 'waiting'
    STATE_QUESTION = 'question'
    STATE_LEADERBOARD = 'leaderboard'
    STATE_ENDED = 'ended'
    STATE_ANSWER_REVEAL = 'answer_reveal'
    STATE_CLOSED = 'closed'
    STATE_CHOICES = [
        (STATE_WAITING, 'Waiting'),
        (STATE_QUESTION, 'Question'),
        (STATE_LEADERBOARD, 'Leaderboard'),
        (STATE_ENDED, 'Ended'),
        (STATE_ANSWER_REVEAL, 'Answer reveal'),
        (STATE_CLOSED, 'Closed'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=8, db_index=True)
    host = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    current_quiz_set = models.ForeignKey('QuizSet', null=True, blank=True, on_delete=models.SET_NULL, related_name='active_sessions')
    current_question_index = models.IntegerField(default=0)  # Track current question within quiz set
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_WAITING, db_index=True)
    current_question = models.ForeignKey('Question', null=True, blank=True, on_delete=models.SET_NULL, related_name='active_sessions')
    timer_duration_seconds = models.IntegerField(default=0)
    state_started_at = models.DateTimeField(null=True, blank=True)
    session_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.code}"

class SessionQuizSet(models.Model):
    session = models.ForeignKey(QuizSession, related_name='quiz_sets', on_delete=models.CASCADE)
    quiz_set = models.ForeignKey(QuizSet, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ['session', 'quiz_set']

    def __str__(self):
        return f"{self.session.code} - {self.quiz_set.title}"

class Participant(models.Model):
    session = models.ForeignKey(QuizSession, related_name='participants', on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    joined_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    total_response_time = models.IntegerField(default=0)  # ms for tie-break
    avatar_id = models.IntegerField(default=0)  # Store selected avatar ID
    avatar_url = models.URLField(blank=True, null=True, max_length=500)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.username} ({self.session.code})"

class AnswerRecord(models.Model):
    participant = models.ForeignKey(Participant, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    correct = models.BooleanField()
    response_time_ms = models.IntegerField()
    answered_at = models.DateTimeField(auto_now_add=True)
