from django.contrib import admin
from .models import Post, Reply, SessionKarma
from .models import Post, Reply, SessionKarma, ModerationQueue

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ('mood_tag', 'category', 'is_approved', 'created_at', 'expires_at')
    list_filter   = ('mood_tag', 'category', 'is_approved')
    search_fields = ('content',)
    ordering      = ('-created_at',)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display  = ('post', 'helpful_votes', 'is_flagged', 'created_at')
    list_filter   = ('is_flagged',)


@admin.register(SessionKarma)
class SessionKarmaAdmin(admin.ModelAdmin):
    list_display = ('session_token', 'karma_points', 'posts_helped', 'week_number')
@admin.register(ModerationQueue)
class ModerationQueueAdmin(admin.ModelAdmin):
    list_display  = ('status', 'reason', 'created_at', 'reviewed_at')
    list_filter   = ('status',)