from django.db import models
from django.utils import timezone
from datetime import timedelta


def default_expiry():
    return timezone.now() + timedelta(days=30)


class Post(models.Model):

    MOOD_CHOICES = [
        ('anxious',    '😰 Anxious'),
        ('sad',        '😔 Sad'),
        ('lost',       '🌀 Lost'),
        ('frustrated', '😤 Frustrated'),
        ('hopeful',    '🌱 Hopeful'),
        ('grateful',   '✨ Grateful'),
    ]

    CATEGORY_CHOICES = [
        ('academic',      'Academic'),
        ('career',        'Career'),
        ('relationships', 'Relationships'),
        ('health',        'Health'),
        ('other',         'Other'),
    ]

    session_token  = models.CharField(max_length=64)
    content        = models.TextField(max_length=500)
    mood_tag       = models.CharField(max_length=20, choices=MOOD_CHOICES)
    category       = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_approved    = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    expires_at     = models.DateTimeField(default=default_expiry)
    karma_received = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.mood_tag}] {self.content[:60]}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class Reply(models.Model):

    post          = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    session_token = models.CharField(max_length=64)
    content       = models.TextField(max_length=300)
    is_flagged    = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to Post #{self.post_id}: {self.content[:40]}"


class SessionKarma(models.Model):

    session_token = models.CharField(max_length=64, unique=True)
    karma_points  = models.IntegerField(default=0)
    posts_helped  = models.IntegerField(default=0)
    week_number   = models.IntegerField(default=0)

    def __str__(self):
        return f"Session karma: {self.karma_points} pts"
class ModerationQueue(models.Model):

    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='moderation_entries', null=True, blank=True)
    reply       = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='moderation_entries', null=True, blank=True)
    reason      = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ModerationQueue [{self.status}] - {self.reason[:40]}"